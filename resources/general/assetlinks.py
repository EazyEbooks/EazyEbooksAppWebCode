from flask import render_template, send_from_directory
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint(
    "asset_links",
    __name__,
    description="assetlinks.json"
)

@blp.route("/.well-known/assetlinks.json")
class AssetLinkPage(MethodView):
    def get(self):
        return send_from_directory('static', 'assetlinks.json')