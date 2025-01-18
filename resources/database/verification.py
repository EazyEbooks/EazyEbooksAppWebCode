from flask import request, render_template
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint(
    "verify_email",
    __name__,
    description="EazyEbooks.com Verification page"
)

@blp.route("/authentication/verify_email")
class EmailVerification(MethodView):
    def get(self):
        email = request.args.get("email")
        return render_template("verification.html", email=email)