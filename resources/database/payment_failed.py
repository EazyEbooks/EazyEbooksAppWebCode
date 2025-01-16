import logging
from flask import request, render_template, redirect, url_for
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint(
    "payment-failed",
    __name__,
    description="EazyEbooks.com Payment Failed page"
)

@blp.route("/payment-failed")
class PaymentFailed(MethodView):
    def get(self):
        ebook_id = request.args.get("ebook_id")
        if not ebook_id:
            logging.error("Missing ebook_id parameter")
            return redirect(url_for("marketplace.Marketplace"))

        return render_template("payment-failed.html", ebook_id=ebook_id)