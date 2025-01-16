from flask import request, render_template
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint(
    "fp-link-sent",
    __name__,
    description="EazyEbooks.com Forgot password link sent page"
)

@blp.route("/password-reset-link")
class PasswordResetLink(MethodView):
    def get(self):
        email = request.args.get("email")
        return render_template("fp-link-sent.html", email=email)