import random
import string
from flask import request, render_template, flash, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import check_password_hash
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from itsdangerous import URLSafeSerializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash

blp = Blueprint(
    "profile_settings",
    __name__,
    description="EazyEbooks.com Profile Settings page"
)

client = MongoClient("mongodb+srv://doadmin:t5iJma1p2I647Y98@db-mongodb-eazy-ebooks-63048b6d.mongo.ondigitalocean.com/eazyebooks?tls=true&authSource=admin&replicaSet=db-mongodb-eazy-ebooks")
db = client["eazyebooks"]
users_collection = db["users"]
password_reset_links_collection = db["password_reset_links"]

serializer = URLSafeSerializer("00ae1987adf41f0d2c421f912e7eecb8e8bdc0d6fc0bb3295b1db934d1b086a4")

def generate_random_string(length=32):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@blp.route("/my-account/profile-settings")
class ProfileSettings(MethodView):
    def get(self):
        if "user_id" not in session:
            return redirect(url_for("login.LoginPage"))
        
        user = users_collection.find_one({"email": session["email"]})
        if user["admin_action"]["suspension"] == True:
            return render_template("suspended.html")
        
        user = users_collection.find_one({"email": session.get("email")})

        full_name = user["full_name"]
        institution = user["institution"]
        general_info = user["general_info"]
        contact_email = user["contact_email"]
        phone_number = user["phone_number"]
        email = session.get("email")

        token = serializer.dumps(email + generate_random_string(), salt="1e16ebce963b6d5f2c62256cee7fa930")
        password_reset_url = url_for("forgot_password.PasswordResetLink", token=token, _external=True)
        print(password_reset_url)

        password_reset_links_collection.insert_one(
            {
                "link": password_reset_url
            }
        )

        return render_template(
            "account-settings.html",
            full_name=full_name,
            institute=institution,
            phone_number=phone_number,
            contact_email=contact_email,
            general_info=general_info,
            email=email,
            password_reset_url=password_reset_url
        )
    
    def post(self):
        if "user_id" not in session:
            return redirect(url_for("login.LoginPage"))
        
        user = users_collection.find_one({"email": session["email"]})
        if user["admin_action"]["suspension"] == True:
            return render_template("suspended.html")
        
        user = users_collection.find_one({"email": session.get("email")})

        form_full_name = request.form.get("name")
        form_institution = request.form.get("institute")
        form_general_info = request.form.get("general-info")
        form_contact_email = request.form.get("contact-email")
        form_phone_number = request.form.get("phone-number")

        full_name = user["full_name"]
        institution = user["institution"]
        general_info = user["general_info"]
        contact_email = user["contact_email"]
        phone_number = user["phone_number"]
        email = user["email"]

        result = users_collection.update_one(
            {"email": email},
            {"$set": {
                "full_name": form_full_name,
                "institution": form_institution,
                "general_info": form_general_info,
                "contact_email": form_contact_email,
                "phone_number": form_phone_number
                }
            }
        )

        full_name = user["full_name"]
        institution = user["institution"]
        general_info = user["general_info"]
        contact_email = user["contact_email"]
        phone_number = user["phone_number"]
        email = user["email"]

        print(f"full name = {form_full_name}")
        print(f"Institution = {form_institution}")
        print(f"general info = {form_general_info}")
        print(f"contact email = {form_contact_email}")
        print(f"phone number = {form_phone_number}")
        print(f"email = {email}")

        token = serializer.dumps(email, salt="1e16ebce963b6d5f2c62256cee7fa930")
        password_reset_url = url_for("forgot_password.PasswordResetLink", token=token, _external=True)
        print(password_reset_url)

        return redirect(url_for(
                "profile_settings.ProfileSettings",
                full_name=full_name,
                institute=institution,
                phone_number=phone_number,
                contact_email=contact_email,
                general_info=general_info,
                email=email,
                password_reset_url=password_reset_url
            )
        )

@blp.route("/logout", methods=["POST"])
class Logout(MethodView):
    def post(self):
        session.clear()
        return redirect(url_for("login.LoginPage"))