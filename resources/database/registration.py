import datetime
import dns.resolver
import smtplib
from typing import Any
from flask import request, render_template, flash, redirect, url_for, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from itsdangerous import URLSafeSerializer, BadSignature, SignatureExpired
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

blp = Blueprint(
    "register",
    __name__,
    description="EazyEbooks.com Registration page"
)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USERNAME = "eazyebooks.contact@gmail.com"
EMAIL_PASSWORD = "hvjqjuhgkcztpowd"

client = MongoClient("mongodb+srv://doadmin:t5iJma1p2I647Y98@db-mongodb-eazy-ebooks-63048b6d.mongo.ondigitalocean.com/eazyebooks?tls=true&authSource=admin&replicaSet=db-mongodb-eazy-ebooks")
db = client["eazyebooks"]
users_collection = db["users"]

serializer = URLSafeSerializer("00ae1987adf41f0d2c421f912e7eecb8e8bdc0d6fc0bb3295b1db934d1b086a4")

try:
    client.server_info()  # This will raise an exception if MongoDB is not reachable
    print("MongoDB connection successful!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
except dns.resolver.LifetimeTimeout:
    print("Your internet is slow")

@blp.route("/register")
class RegistrationPage(MethodView):
    def get(self):
        return render_template("register.html")
    
    def post(self):
        print("Post request received")
        full_name = request.form.get("full-name")
        email = request.form.get("email")
        degree = request.form.get("degree")
        institution = request.form.get("institution")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        if not full_name or not email or not degree or not institution or not password or not confirm_password:
            flash("All fields are required")
            
            return redirect(url_for("register.RegistrationPage"))
        
        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for("register.RegistrationPage"))
        
        if users_collection.find_one({"email": email}):
            flash("An account with this email already exists")
            return redirect(url_for("register.RegistrationPage"))
        
        email_domain = email.split("@")[-1]
        email_validity = False

        if email_validity == True:pass

        try:
            records = dns.resolver.resolve(email_domain, "MX")
            email_validity = True if records else False
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            email_validity = False
        except dns.resolver.LifetimeTimeout:
            return "Your internet is slow"
        
        user_data = {
            "full_name": full_name,
            "email": email,
            "degree": degree,
            "institution": institution,
            "password": generate_password_hash(password),
            "contact_email": "",
            "phone_number": "",
            "general_info": "",
            "created_at": datetime.datetime.now().strftime(f"%d %B, %Y (%I.%M %p)").replace("AM", "am").replace("PM", "pm"),
            "active": False,
            "library": [],
            "admin_action": {
                "suspension": False
            }
        }

        print(user_data)

        try:
            users_collection.insert_one(user_data)
            token = serializer.dumps(email, salt="1e16ebce963b6d5f2c62256cee7fa930")
            print(token)
            activation_link = url_for("register.ActivateAccount", token=token, _external=True)

            subject = f"EazyEbooks - Activate your account"
            body = render_template(
                "account-activation-link-email-template.html",
                activation_url=activation_link
            )

            msg = MIMEMultipart()
            msg["From"] = EMAIL_USERNAME
            msg["To"] = email
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "html"))

            try:
                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                    server.starttls()
                    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                    server.sendmail(EMAIL_USERNAME, email, msg.as_string())
                flash("Thank you for reaching out! We'll get back to you soon.", "success")
            except Exception as e:
                flash(f"An error occurred: {e}", "error")

            # print(activation_link)

        except Exception as e:
            print(e)

        return redirect(url_for("verify_email.EmailVerification", email=email))
    
@blp.route("/authentication/activate-account/<token>")
class ActivateAccount(MethodView):
    def get(self, token):
        try:
            email = serializer.loads(token, salt="1e16ebce963b6d5f2c62256cee7fa930", max_age=3600)

            user = users_collection.find_one({"email": email})
            name = user["full_name"]

            if not user:
                message = "Invalid activation link"
                return render_template("activation-link.html", message=message)
            
            if user.get("active"):
                message = "Account is already active"

                return render_template("activation-link.html", full_name=name, message=message) # REDIRECT TO LOGIN
            users_collection.update_one({"email": email}, {"$set": {"active": True}})
            message = "Account Activated"

            return render_template("activation-link.html", full_name=name, message=message) #REDIRECT TO LOGIN
        
        except SignatureExpired:
            flash("The activation link has expired. Please register again.")
            return redirect(url_for("register.RegistrationPage"))
        except BadSignature:
            flash("Invalid activation link!")
            return redirect(url_for("register.RegistrationPage"))