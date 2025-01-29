from flask import request, render_template, url_for, redirect, session
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta

blp = Blueprint(
    "home",
    __name__,
    description="EazyEbooks app's Home page"
)

client = MongoClient("mongodb+srv://doadmin:t5iJma1p2I647Y98@db-mongodb-eazy-ebooks-63048b6d.mongo.ondigitalocean.com/eazyebooks?tls=true&authSource=admin&replicaSet=db-mongodb-eazy-ebooks")
db = client["eazyebooks"]
ebooks_collection = db["ebooks"]
users_collection = db["users"]

@blp.route("/")
class Home(MethodView):
    def get(self):
        if "user_id" not in session:
            return redirect(url_for("get_started.get_started"))
        
        user = users_collection.find_one({"email": session["email"]})
        if user["admin_action"]["suspension"] == True:
            return render_template("suspended.html")
        
        print(f"User ID: {session['user_id']}")
        
        user = users_collection.find_one({"_id": ObjectId(session["user_id"])})
        if user is None:
            return redirect(url_for("get_started.get_started"))
        
        user_library = user.get("library", [])
        detailed_library = []

        for book in user_library:
            ebook = ebooks_collection.find_one({"name": book["ebook"]})
            if ebook:
                expiry_date = datetime.strptime(book["expiry_date"], "%Y-%m-%d")
                if expiry_date > datetime.now():
                    ebook["purchase_date"] = book["purchase_date"]
                    ebook["expiry_date"] = book["expiry_date"]
                    detailed_library.append(ebook)

        return render_template(
            "home.html",
            user_library=detailed_library,
            name=session["user_name"]
        )