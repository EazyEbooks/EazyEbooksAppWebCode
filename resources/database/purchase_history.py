from flask import request, render_template, session, flash, redirect, url_for
from flask.views import MethodView
from flask_smorest import Blueprint
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

blp = Blueprint(
    "purchase_history",
    __name__,
    description="EazyEbooks.com Purchase History page"
)

client = MongoClient("mongodb+srv://doadmin:t5iJma1p2I647Y98@db-mongodb-eazy-ebooks-63048b6d.mongo.ondigitalocean.com/eazyebooks?tls=true&authSource=admin&replicaSet=db-mongodb-eazy-ebooks")
db = client["eazyebooks"]
users_collection = db["users"]

@blp.route("/purchase-history")
class PurchaseHistory(MethodView):
    def get(self):
        if "user_id" not in session:
            return redirect(url_for("login.LoginPage"))
        
        user = users_collection.find_one({"email": session["email"]})
        if user["admin_action"]["suspension"] == True:
            return render_template("suspended.html")
        
        user = users_collection.find_one({"_id": ObjectId(session["user_id"])})
        library = user.get("library", [])
        pending_orders = user.get("pending_orders", [])

        return render_template("purchase-history.html", library=library, pending_orders=pending_orders, datetime=datetime)

@blp.route("/purchase-history/request-refund/<ebook>", methods=["POST"])
class RequestRefund(MethodView):
    def post(self, ebook):
        if "user_id" not in session:
            return redirect(url_for("login.LoginPage"))
        
        user = users_collection.find_one({"email": session["email"]})
        if user["admin_action"]["suspension"] == True:
            return render_template("suspended.html")
        
        user = users_collection.find_one({"_id": ObjectId(session["user_id"])})
        for item in user["library"]:
            if item["ebook"] == ebook:
                if (datetime.datetime.now() - datetime.datetime.strptime(item["purchase_date"], '%Y-%m-%d')).days <= 3 and not item.get("accessed", False):
                    item["refund"] = True
                    users_collection.update_one({"_id": ObjectId(session["user_id"])}, {"$set": {"library": user["library"]}})
                    flash("Refund requested successfully.")
                else:
                    flash("Refund cannot be requested.")
                break

        return redirect(url_for("purchase_history.PurchaseHistory"))

@blp.route("/purchase-history/request-refund-hardcopy/<order_id>", methods=["POST"])
class RequestRefundHardCopy(MethodView):
    def post(self, order_id):
        if "user_id" not in session:
            return redirect(url_for("login.LoginPage"))
        
        user = users_collection.find_one({"email": session["email"]})
        if user["admin_action"]["suspension"] == True:
            return render_template("suspended.html")
        
        refund_reason = request.form.get("refund_reason")
        user = users_collection.find_one({"_id": ObjectId(session["user_id"])})
        for order in user["pending_orders"]:
            if str(order["_id"]) == order_id:
                if (datetime.datetime.now() - datetime.datetime.strptime(order["order_placement_date"], '%Y-%m-%d')).days <= 7:
                    order["refund_requested"] = True
                    order["refund_reason"] = refund_reason
                    users_collection.update_one({"_id": ObjectId(session["user_id"])}, {"$set": {"pending_orders": user["pending_orders"]}})
                    flash("Refund requested successfully.")
                else:
                    flash("Refund cannot be requested.")
                break

        return redirect(url_for("purchase_history.PurchaseHistory"))
