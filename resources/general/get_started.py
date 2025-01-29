from flask import render_template
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint(
    "get_started",
    __name__,
    description="Get Started page"
)

@blp.route("/get-started")
def get_started():
    return render_template("get-started.html")
