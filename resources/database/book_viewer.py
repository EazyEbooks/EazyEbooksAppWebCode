from flask import request, render_template, url_for, redirect, session
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from pymongo import MongoClient
from bson.objectid import ObjectId

blp = Blueprint(
    "book_viewer",
    __name__,
    description="EazyEbooks.com Book Viewer page"
)

client = MongoClient("mongodb+srv://doadmin:t5iJma1p2I647Y98@db-mongodb-eazy-ebooks-63048b6d.mongo.ondigitalocean.com/eazyebooks?tls=true&authSource=admin&replicaSet=db-mongodb-eazy-ebooks")
db = client["eazyebooks"]
ebooks_collection = db["ebooks"]
users_collection = db["users"]

@blp.before_request
def make_session_permanent():
    session.permanent = True

@blp.route("/library/read/<ebook_id>")
class Read(MethodView):
    def get(self, ebook_id):
        if "user_id" not in session:
            return redirect(url_for("login.LoginPage"))
        
        user = users_collection.find_one({"_id": ObjectId(session["user_id"])})
        if user is None:
            return redirect(url_for("login.LoginPage"))
        
        user = users_collection.find_one({"email": session["email"]})
        if user["admin_action"]["suspension"] == True:
            return render_template("suspended.html")

        try:
            ebook = ebooks_collection.find_one({"document_id": ebook_id})
        except Exception as e:
            print(f"Error querying database: {e}")
            abort(500, message="Internal Server Error")

        if not ebook:
            abort(404, message="Book not found")

        # Check if the book is in the user's library
        book_in_library = None
        for book in user.get("library", []):
            if book["ebook"] == ebook["name"]:
                book_in_library = book
                break

        if not book_in_library:
            return redirect(url_for("marketplace.BuyEbook", ebook_id=ebook_id))

        # Set the accessed field to True
        users_collection.update_one(
            {"_id": ObjectId(session["user_id"]), "library.ebook": ebook["name"]},
            {"$set": {"library.$.accessed": True}}
        )

        return render_template(
            "book-viewer.html",
            ebook_id=ebook_id
        )