from flask import render_template, session, redirect, url_for
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from pymongo import MongoClient

blp = Blueprint(
    "get_started",
    __name__,
    description="Get Started page"
)

client = MongoClient("mongodb+srv://doadmin:t5iJma1p2I647Y98@db-mongodb-eazy-ebooks-63048b6d.mongo.ondigitalocean.com/eazyebooks?tls=true&authSource=admin&replicaSet=db-mongodb-eazy-ebooks")
db = client["eazyebooks"]
users_collection = db["users"]

@blp.before_request
def make_session_permanent():
    session.permanent = True

@blp.route("/get-started")
def get_started():
    if "user_id" in session:
        return redirect(url_for("home.Home"))
    
    return render_template("get-started.html")
