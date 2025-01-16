from flask import request, render_template, flash, redirect, url_for
from flask.views import MethodView
from flask_smorest import Blueprint
from pymongo import MongoClient
from itsdangerous import URLSafeSerializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash

blp = Blueprint(
    "password_reset_link",
    __name__,
    description="EazyEbooks.com Password Reset Link Page"
)

client = MongoClient("mongodb+srv://doadmin:t5iJma1p2I647Y98@db-mongodb-eazy-ebooks-63048b6d.mongo.ondigitalocean.com/eazyebooks?tls=true&authSource=admin&replicaSet=db-mongodb-eazy-ebooks")
db = client["eazyebooks"]
users_collection = db["users"]

serializer = URLSafeSerializer("00ae1987adf41f0d2c421f912e7eecb8e8bdc0d6fc0bb3295b1db934d1b086a4")


@blp.route("/reset-password/<token>")
class PasswordResetLink(MethodView):
    def get(self, token):
        try:
            email = serializer.loads(token, salt="1e16ebce963b6d5f2c62256cee7fa930", max_age=3600)

            user = users_collection.find_one({"email": email})
            if not user:
                flash("Invalid reset link.")
                return render_template("reset-password.html")

        except SignatureExpired:
            flash("The reset link has expired. Please request a new one.")
            return render_template("reset-password.html")

        except BadSignature:
            flash("Invalid reset link!")
            return render_template("reset-password.html")

        return render_template("reset-password.html", email=email)

    def post(self, token):
        try:
            email = serializer.loads(token, salt="1e16ebce963b6d5f2c62256cee7fa930", max_age=3600)

            password = request.form.get("password")
            confirm_password = request.form.get("retype-password")

            if password != confirm_password:
                flash("The password values do not match.")
                return render_template("reset-password.html")

            result = users_collection.update_one(
                {"email": email},
                {"$set": {"password": generate_password_hash(password)}}
            )

            if result.matched_count > 0:
                flash("Password successfully updated.")
                return render_template("reset-password.html") #Redirect to password-successfully-changed.html

        except SignatureExpired:
            flash("The reset link has expired. Please request a new one.")
            return render_template("reset-password.html")
        except BadSignature:
            flash("Invalid reset link!")
            return render_template("reset-password.html")
