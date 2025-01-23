from flask import request, render_template, flash, redirect, url_for, session, current_app
from pymongo import MongoClient
from werkzeug.security import check_password_hash
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from datetime import datetime, timezone
import logging

blp = Blueprint(
    "login",
    __name__,
    description="EazyEbooks.com Login page"
)

client = MongoClient("mongodb+srv://doadmin:t5iJma1p2I647Y98@db-mongodb-eazy-ebooks-63048b6d.mongo.ondigitalocean.com/eazyebooks?tls=true&authSource=admin&replicaSet=db-mongodb-eazy-ebooks")
db = client["eazyebooks"]
users_collection = db["users"]

@blp.before_request
def make_session_permanent():
    session.permanent = True

@blp.route("/login")
class LoginPage(MethodView):
    def get(self):
        if "user_id" in session:
            return redirect(url_for("home.Home"))
        
        return render_template("login.html")
    
    def post(self):
        email = request.form.get("email")
        password = request.form.get("password")

        user = users_collection.find_one({"email": email})

        if user and check_password_hash(user["password"], password):
            if user.get("active_session"):
                return redirect(url_for("login.AccountActivePage"))
            
            session["user_id"] = str(user["_id"])
            session["email"] = user["email"]
            session["user_name"] = user["full_name"]
            users_collection.update_one(
                {"email": email},
                {"$set": {"active_session": True, "last_activity": datetime.now(timezone.utc).isoformat()}}
            )
            logging.info(f"User {email} logged in successfully.")
            return redirect(url_for("home.Home"))
        else:
            logging.warning(f"Failed login attempt for email: {email}")
            return render_template("login.html", error="Invalid email or password")

@blp.route("/logout")
class LogoutPage(MethodView):
    def get(self):
        if "user_id" in session:
            logging.info(f"Logging out user: {session['email']}")
            users_collection.update_one({"email": session["email"]}, {"$set": {"active_session": False}})
            session.clear()
        return redirect(url_for("login.LoginPage"))

@blp.route("/account-active")
class AccountActivePage(MethodView):
    def get(self):
        return render_template("account_active.html")
