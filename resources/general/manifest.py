from flask import render_template, send_from_directory
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint(
    "manifest",
    __name__,
    description="manifest.json"
)

@blp.route("/manifest.json")
class ManifestPage(MethodView):
    def get(self):
        return send_from_directory('static', 'manifest.json')