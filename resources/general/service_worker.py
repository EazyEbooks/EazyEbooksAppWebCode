from flask import render_template, send_from_directory
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint(
    "service_worker",
    __name__,
    description="service-worker.js"
)

@blp.route("/service-worker.js")
class ServiceWorkerJs(MethodView):
    def get(self):
        return send_from_directory('static', 'service-worker.js')