from flask import request, render_template, Response
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint(
    "ads",
    __name__,
    description="EazyEbooks.com ads.txt page"
)

@blp.route("/ads.txt")
class AdsTxt(MethodView):
    def get(self):
        content = "google.com, pub-8875422219223826, DIRECT, f08c47fec0942fa0"
        return Response(content, mimetype="text/plain")