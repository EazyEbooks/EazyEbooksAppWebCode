from flask import request, render_template, flash, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import check_password_hash
from flask.views import MethodView
from flask_smorest import Blueprint, abort

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
        return render_template("login.html")
    
    def post(self):
        email = request.form.get("email")
        password = request.form.get("password")

        print(f"Email entered: {email}, Password entered: {password}")

        if not email or not password:
            flash("Both email and password fields are required")
            return redirect(url_for("login.LoginPage"))
        
        user = users_collection.find_one({"email": email})
        print(f"User found: {user}")

        if not user:
            flash("An user with this email does not exist!")
            return redirect(url_for("login.LoginPage"))
        
        if not check_password_hash(user["password"], password):
            flash("Invalid email or password")
            return redirect(url_for("login.LoginPage"))
        
        session.clear()
        session["user_id"] = str(user["_id"])
        session["email"] = user["email"]
        session["user_name"] = user["full_name"]

        print(f"Session created for user ID: {session['user_id']}, Name: {session['user_name']}")
        return redirect(url_for("home.Home"))
