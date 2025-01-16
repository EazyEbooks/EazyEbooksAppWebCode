from flask import request, render_template, url_for, redirect, session
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from pymongo import MongoClient
from bson.objectid import ObjectId

blp = Blueprint(
    "user_order",
    __name__,
    description="EazyEbooks.com User Orders page"
)

client = MongoClient("mongodb+srv://doadmin:t5iJma1p2I647Y98@db-mongodb-eazy-ebooks-63048b6d.mongo.ondigitalocean.com/eazyebooks?tls=true&authSource=admin&replicaSet=db-mongodb-eazy-ebooks")
db = client["eazyebooks"]
users_collection = db["users"]

@blp.route("/my-orders")
class UserOrders(MethodView):
    def get(self):
        if "user_id" not in session:
            return redirect(url_for("login.LoginPage"))

        user = users_collection.find_one({"_id": ObjectId(session["user_id"])})
        if not user:
            return redirect(url_for("login.LoginPage"))
        
        user = users_collection.find_one({"email": session["email"]})
        if user["admin_action"]["suspension"] == True:
            return render_template("suspended.html")

        orders = user.get("pending_orders", [])

        return render_template(
            "your-order.html",
            name=session["user_name"],
            orders=orders
        )
