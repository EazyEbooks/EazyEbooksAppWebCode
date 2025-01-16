import logging
from flask import request, render_template, redirect, url_for
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint(
    "payment-success",
    __name__,
    description="EazyEbooks.com Payment Successful page"
)

@blp.route("/payment-success")
class PaymentSuccess(MethodView):
    def get(self):
        return render_template("payment-success.html")
    
@blp.route("/order-success")
class OrderSuccess(MethodView):
    def get(self):
        return render_template("hard-copt-payment-success.html")