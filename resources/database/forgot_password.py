import dns.resolver
import random
import string
import smtplib
from flask import request, render_template, session, flash, redirect, url_for
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from pymongo import MongoClient
from itsdangerous import URLSafeSerializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

blp = Blueprint(
    "forgot_password",
    __name__,
    description="EazyEbooks.com Forgot Password page"
)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USERNAME = "eazyebooks.contact@gmail.com"
EMAIL_PASSWORD = "hvjqjuhgkcztpowd"

client = MongoClient("mongodb+srv://doadmin:t5iJma1p2I647Y98@db-mongodb-eazy-ebooks-63048b6d.mongo.ondigitalocean.com/eazyebooks?tls=true&authSource=admin&replicaSet=db-mongodb-eazy-ebooks")

db = client["eazyebooks"]
users_collection = db["users"]
password_reset_links_collection = db["password_reset_links"]

serializer = URLSafeSerializer("00ae1987adf41f0d2c421f912e7eecb8e8bdc0d6fc0bb3295b1db934d1b086a4")

def generate_random_string(length=32):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@blp.route("/forgot-password")
class ForgotPassword(MethodView):
    def get(self):
        return render_template("forgot-password.html")
    
    def post(self):
        email = request.form.get("email")

        if not email:
            flash("Please enter the email address")
            # return render_template("forgot-password.html")

            return redirect(url_for("forgot_password.ForgotPassword"))
        
        if not users_collection.find_one({"email": email}):
            flash("An account with this email does not exist")
            # return render_template("forgot-password.html")


            return redirect(url_for("forgot_password.ForgotPassword")) #redirect to "we have send a password reset link to your email address"

        token = serializer.dumps(email + generate_random_string(), salt="1e16ebce963b6d5f2c62256cee7fa930")
        password_reset_url = url_for("forgot_password.PasswordResetLink", token=token, _external=True)
        print(password_reset_url)

        password_reset_links_collection.insert_one(
            {
                "link": password_reset_url
            }
        )

        user = users_collection.find_one({"email": email})

        subject = f"EazyEbooks - Reset your password"
        body = render_template(
            "password-reset-link-email-template.html",
            user_name=user["full_name"],
            reset_password_link=password_reset_url
        )

        msg = MIMEMultipart()
        msg["From"] = EMAIL_USERNAME
        msg["To"] = email  # Send to yourself or the designated email
        msg["Subject"] = subject

        # Attach the HTML email body
        msg.attach(MIMEText(body, "html"))

        try:
            # Connect to the SMTP server and send the email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()  # Secure the connection
                server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                server.sendmail(EMAIL_USERNAME, email, msg.as_string())

                print("email sent")
            flash("Thank you for reaching out! We'll get back to you soon.", "success")
        except Exception as e:
            flash(f"An error occurred: {e}", "error")


        return redirect(url_for("fp-link-sent.PasswordResetLink", email=email))
    
@blp.route("/reset-password/<token>")
class PasswordResetLink(MethodView):
    def get(self, token):
        if password_reset_links_collection.find_one({"link":url_for("forgot_password.PasswordResetLink", token=token, _external=True)}):
            try:
                email = serializer.loads(token, salt="1e16ebce963b6d5f2c62256cee7fa930", max_age=3600)[:-32]

                user = users_collection.find_one({"email": email})
                if not user:
                    message = "Invalid reset link!"
                    return render_template("reset-password.html", endpoint=f"/reset-password/{token}", message=message)

            except SignatureExpired:
                message = "This reset link has expired"
                return render_template("reset-password.html" ,endpoint=f"/reset-password/{token}", message=message)

            except BadSignature:
                message = "Invalid reset link!"
                return render_template("reset-password.html", endpoint=f"/reset-password/{token}", message=message)

            return render_template("reset-password.html", email=email, endpoint=f"/reset-password/{token}")
        
        else:
            message = "Invalid reset link!"
            return render_template("reset-password.html", message=message)

    def post(self, token):
        if password_reset_links_collection.find_one({"link":url_for("forgot_password.PasswordResetLink", token=token, _external=True)}):
            try:
                email = serializer.loads(token, salt="1e16ebce963b6d5f2c62256cee7fa930", max_age=3600)[:-32]

                password = request.form.get("password")
                confirm_password = request.form.get("retype-password")

                print(password)
                print(confirm_password)

                if password != confirm_password:
                    flash("The password values do not match.")
                    return render_template("reset-password.html")

                result = users_collection.update_one(
                    {"email": email},
                    {"$set": {"password": generate_password_hash(password)}}
                )

                if result.matched_count > 0:
                    message = "Password successfully updated"
                    print(message)

                    session.clear()

                    password_reset_links_collection.delete_one({"link": url_for("forgot_password.PasswordResetLink", token=token, _external=True)})

                    return redirect(url_for("forgot_password.PasswordResetSuccessfully")) #Redirect to password-successfully-changed.html
                
                else:
                    message = "Sorry, something went wrong!"
                    print(message)

                    password_reset_links_collection.delete_one({"link": url_for("forgot_password.PasswordResetLink", token=token, _external=True)})

                    return render_template("reset-password.html", email=email)


            except SignatureExpired:
                message = "This reset link has expired"
                return render_template("reset-password.html", message=message)
            except BadSignature:
                message = "Invalid reset link!"
                return render_template("reset-password.html", message=message)
            
        else:
            message = "Invalid reset link!"
            return render_template("reset-password.html", message=message)
        
@blp.route("/password-reset-successfully")
class PasswordResetSuccessfully(MethodView):
    def get(self):
        return render_template("password-reset-successfully.html")