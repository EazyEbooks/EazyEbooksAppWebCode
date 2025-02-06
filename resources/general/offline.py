from flask import render_template
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint(
    "offline",
    __name__,
    description="Offline page"
)

@blp.route("/offline")
class OfflinePage(MethodView):
    def get(self):
        return render_template("offline.html")