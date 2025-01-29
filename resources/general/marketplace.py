import razorpay
import logging
import hashlib
import hmac
from flask import request, render_template, url_for, redirect, session, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from pymongo import MongoClient
from datetime import datetime, timedelta

import razorpay.errors

blp = Blueprint(
    "marketplace",
    __name__,
    description="EazyEbooks.com Marketplace page"
)

client = MongoClient("mongodb+srv://doadmin:t5iJma1p2I647Y98@db-mongodb-eazy-ebooks-63048b6d.mongo.ondigitalocean.com/eazyebooks?tls=true&authSource=admin&replicaSet=db-mongodb-eazy-ebooks")
db = client["eazyebooks"]
ebooks_collection = db["ebooks"]
users_collection = db["users"]

razorpay_key_id = "rzp_live_A2qFKIIV3Tgi7i"
razorpay_key_secret = "DfBygPgNXuH1Avpzx4MNwGJY"

razorpay_client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))

@blp.before_request
def make_session_permanent():
    session.permanent = True

@blp.route("/marketplace")
class Marketplace(MethodView):
    def get(self):
        if "user_id" not in session:
            return redirect(url_for("login.LoginPage"))
        
        elif "user_id" in session:
            user = users_collection.find_one({"email": session["email"]})
            if user["admin_action"]["suspension"] == True:
                return render_template("suspended.html")
            logging.info(f"User ID: {session['user_id']}")

            degree = request.args.get('degree')
            university = request.args.get('university')
            year = request.args.get('year')
            search = request.args.get('search')

            query = {}
            if degree:
                query['additional_info.degree'] = {'$regex': degree, '$options': 'i'}
            if university:
                query['additional_info.university'] = {'$regex': university, '$options': 'i'}
            if year:
                query['additional_info.year'] = {'$regex': year, '$options': 'i'}
            if search:
                query['name'] = {'$regex': search, '$options': 'i'}

            ebook_documents = []

            try:
                cursor = ebooks_collection.find(query)
                for single_ebook_document in cursor:
                    ebook_documents.append(single_ebook_document)
                logging.info(f"Ebooks: {ebook_documents}")
            except Exception as e:
                logging.error(f"Error fetching ebooks: {e}")
                abort(500, message="Internal Server Error")

            return render_template(
                "marketplace.html",
                name=session["user_name"],
                ebook_documents=ebook_documents,
                degree=degree,
                university=university,
                year=year,
                search=search
            )

@blp.route("/marketplace-test")
class MarketplaceTest(MethodView):
    def get(self):
        if "user_id" not in session:
            return redirect(url_for("login.LoginPage"))
        
        elif "user_id" in session:
            user = users_collection.find_one({"email": session["email"]})
            if user["admin_action"]["suspension"] == True:
                return render_template("suspended.html")
            logging.info(f"User ID: {session['user_id']}")

            degree = request.args.get('degree')
            university = request.args.get('university')
            year = request.args.get('year')

            query = {}
            if degree:
                query['additional_info.degree'] = {'$regex': f'^{degree}$', '$options': 'i'}
            if university:
                query['additional_info.university'] = {'$regex': f'^{university}$', '$options': 'i'}
            if year:
                query['additional_info.year'] = {'$regex': f'^{year}$', '$options': 'i'}

            ebook_documents = []

            try:
                cursor = ebooks_collection.find(query)
                for single_ebook_document in cursor:
                    ebook_documents.append(single_ebook_document)
                logging.info(f"Ebooks: {ebook_documents}")
            except Exception as e:
                logging.error(f"Error fetching ebooks: {e}")
                abort(500, message="Internal Server Error")

            return render_template(
                "marketplace.html",
                name=session["user_name"],
                ebook_documents=ebook_documents,
                degree=degree,
                university=university,
                year=year
            )
        
@blp.route("/marketplace/buy/<ebook_id>")
class BuyEbook(MethodView):
    def get(self, ebook_id):
        if "user_id" not in session:
            return redirect(url_for("login.LoginPage"))

        user = users_collection.find_one({"email": session["email"]})
        if user["admin_action"]["suspension"] == True:
            return render_template("suspended.html")
        
        session["ebook_id"] = ebook_id

        logging.info(f"GET REQ {session['ebook_id']}")

        try:
            ebook = ebooks_collection.find_one({"document_id": ebook_id})
            if not ebook:
                abort(404, message="Ebook not found")

        except Exception as e:
            logging.error(f"Error fetching ebook: {e}")
            abort(500, message="Internal Server Error")

        receipt_id = f"order_rcptid_{session['email']}_{ebooks_collection.find_one({'document_id': ebook_id})['name']}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        try:
            razorpay_order = razorpay_client.order.create(
                {
                    "amount": int(ebook['discounted_price']) * 100,
                    "currency": "INR",
                    # "recipt": receipt_id
                }
            )

        except Exception as e:
            logging.error(f"Error creating Razorpay order: {e}")
            abort(
                500,
                message="Internal Server Error"
            )

        book_purchased = 0
        user = users_collection.find_one({"email": session["email"]})
        if ebook["name"] in [library_item["ebook"] for library_item in user["library"]]:
            book_purchased = 1

        print(f"Ebook ===== {ebook['hard-copy-availability']}")

        return render_template(
            "buyebook.html",
            book_purchased=book_purchased,
            ebook=ebook,
            name=session["user_name"],
            razorpay_key_id=razorpay_key_id,
            user={
                "name": session["user_name"],
                "email": session["email"],
            },
            order_id=razorpay_order["id"]
        )
    
@blp.route("/marketplace/buy/<ebook_id>/add-shipping-address")
class AddShippingAddress(MethodView):
    def get(self, ebook_id):
        if "user_id" not in session:
            return redirect(url_for("login.LoginPage"))
        
        else:
            user = users_collection.find_one({"email": session["email"]})
            if user["admin_action"]["suspension"] == True:
                return render_template("suspended.html")

            session["ebook_id"] = ebook_id
            return render_template(
                "add-shipping-address.html",
                name=session["user_name"],
                ebook_id=ebook_id
            )
    
    def post(self, ebook_id):
        if "user_id" not in session:
            return redirect(url_for("login.LoginPage"))
        
        else:
            user = users_collection.find_one({"email": session["email"]})
            if user["admin_action"]["suspension"] == True:
                return render_template("suspended.html")
            shipping_address = {
                "full_name": request.form.get("full_name"),
                "email_address": request.form.get("email_address"),
                "mobile_number": request.form.get("mobile_number"),
                "address": request.form.get("address"),
                "city": request.form.get("city"),
                "state": request.form.get("state")
            }

            session["shipping_address"] = shipping_address

            return redirect(url_for("marketplace.OrderOverview", ebook_id=ebook_id))
        
@blp.route("/marketplace/buy/<ebook_id>/order-overview")
class OrderOverview(MethodView):
    def get(self, ebook_id):
        if "user_id" not in session:
            return redirect(url_for("login.LoginPage"))
        
        elif "user_id" in session:
            user = users_collection.find_one({"email": session["email"]})
            if user["admin_action"]["suspension"] == True:
                return render_template("suspended.html")

            session["ebook_id"] = ebook_id
            try:
                ebook = ebooks_collection.find_one({"document_id": ebook_id})
                if not ebook:
                    abort(404, message="Ebook not found")
            except Exception as e:
                logging.error(f"Error fetching ebook: {e}")
                print(e)
                abort(500, message="Internal Server Error. E 1")

            try:
                shipping_address = session["shipping_address"]
                if not shipping_address:
                    return redirect(url_for("marketplace.AddShippingAddress", ebook_id=ebook_id))
                
            except KeyError:
                return redirect(url_for("marketplace.AddShippingAddress", ebook_id=ebook_id))
            
            try:
                razorpay_order = razorpay_client.order.create(
                    {
                        "amount": int(ebook['discounted_price_hard_copy']) * 100,
                        "currency": "INR",
                        # "recipt": receipt_id
                    }
                )

            except Exception as e:
                logging.error(f"Error creating Razorpay order: {e}")
                print(e)
                abort(
                    500,
                    message="Internal Server Error E 2"
                )

            user = users_collection.find_one({"email": session["email"]})
            session["delivery_address"] = shipping_address
            
            return render_template(
                "order-overview.html",
                name=session["user_name"],
                ebook=ebook,
                razorpay_key_id=razorpay_key_id,
                user={
                    "name": session["user_name"],
                    "email": session["email"],
                },
                order_id=razorpay_order["id"],
                shipping_address=session["shipping_address"]
            )
        
    
@blp.route("/marketplace/purchase/<ebook_id>/payment-verification", methods=["POST"])
class PaymentVerification(MethodView):
    def post(self, ebook_id):
        payment_data = request.json
        print(f"Payment Data Received: {payment_data}")
        logging.info(f"Payment Data Received: {payment_data}")

        razorpay_order_id = payment_data.get("razorpay_order_id")
        razorpay_payment_id = payment_data.get("razorpay_payment_id")
        razorpay_signature = payment_data.get("razorpay_signature")

        if not (razorpay_order_id and razorpay_payment_id and razorpay_signature):
            logging.error("Missing payment details in request data")
            return jsonify({"error": "Invalid payment data"}), 400
        
        parameters = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }

        try:
            # razorpay.utility.Utility.verify_payment_signature(parameters)
            # razorpay_client.utility.verify_payment_signature(parameters)
            # logging.info("Payment signature verified successfully")

            message = f"{razorpay_order_id}|{razorpay_payment_id}".encode()
            expected_signature = hmac.new(
                razorpay_key_secret.encode(), message, hashlib.sha256
            ).hexdigest()
            
            logging.info(f"Expected Signature: {expected_signature}")
            logging.info(f"Received Signature: {razorpay_signature}")

            print("######## reached here ########")
            print(f"Expected Signature: {expected_signature}")
            print(f"Received Signature: {razorpay_signature}")
            print(expected_signature == razorpay_signature)

            if expected_signature != razorpay_signature:
                logging.error("Signature mismatch")
                print("######## Signature mismatch #######")
                print(f"Expected signature: {expected_signature} & razorpay signature: {razorpay_signature}")
                return jsonify({"error": "Signature mismatch"}), 400

            logging.info("Payment signature verified successfully")

            email = session["email"]

            purchase_date = datetime.now()
            expiry_date = purchase_date + timedelta(days=180)

            ebook = ebooks_collection.find_one({"document_id": ebook_id})

            library_entry = {
                "ebook": ebook["name"],
                "purchase_date": purchase_date.strftime("%Y-%m-%d"),
                "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                "amount": ebook["discounted_price"],
                "accessed": False,
                "refund": False
            }

            user = users_collection.find_one({"email": email})
            purchased = False

            for library_item in user["library"]:
                if library_item["ebook"] == ebook["name"]:
                    purchased = True
                    break

            if not purchased:
                users_collection.update_one(
                    {"email": email},
                    {
                        "$push": {
                            "library": library_entry
                        }
                    }
                )

            else:
                print("######## Ebook already purchased ########")
                return jsonify({"error": "Ebook already purchased"}), 400

            # return redirect(url_for("payment-success.PaymentSuccess"))
            return jsonify({"message": "Payment Successful"}), 200
        
        except razorpay.errors.SignatureVerificationError:
            # return redirect(url_for("payment-failed.PaymentFailed"))
            return jsonify({"error": "Payment Verification failed"}), 400


@blp.route("/marketplace/purchase/hard-copy/<ebook_id>/payment-verification", methods=["POST"])
class PaymentVerificationHardCopy(MethodView):
    def post(self, ebook_id):
        payment_data = request.json
        print(f"Payment Data Received: {payment_data}")
        logging.info(f"Payment Data Received: {payment_data}")

        razorpay_order_id = payment_data.get("razorpay_order_id")
        razorpay_payment_id = payment_data.get("razorpay_payment_id")
        razorpay_signature = payment_data.get("razorpay_signature")

        if not (razorpay_order_id and razorpay_payment_id and razorpay_signature):
            logging.error("Missing payment details in request data")
            return jsonify({"error": "Invalid payment data"}), 400
        
        parameters = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }

        try:
            # razorpay.utility.Utility.verify_payment_signature(parameters)
            # razorpay_client.utility.verify_payment_signature(parameters)
            # logging.info("Payment signature verified successfully")

            message = f"{razorpay_order_id}|{razorpay_payment_id}".encode()
            expected_signature = hmac.new(
                razorpay_key_secret.encode(), message, hashlib.sha256
            ).hexdigest()
            
            logging.info(f"Expected Signature: {expected_signature}")
            logging.info(f"Received Signature: {razorpay_signature}")

            print("######## reached here ########")
            print(f"Expected Signature: {expected_signature}")
            print(f"Received Signature: {razorpay_signature}")
            print(expected_signature == razorpay_signature)

            if expected_signature != razorpay_signature:
                logging.error("Signature mismatch")
                print("######## Signature mismatch #######")
                print(f"Expected signature: {expected_signature} & razorpay signature: {razorpay_signature}")
                return jsonify({"error": "Signature mismatch"}), 400

            logging.info("Payment signature verified successfully")

            email = session["email"]

            order_placement_date = datetime.now()

            ebook = ebooks_collection.find_one({"document_id": ebook_id})

            order_entry = {
                "ebook": ebook["name"],
                "order_placement_date": order_placement_date.strftime("%Y-%m-%d"),
                "delivery_address": session["delivery_address"],
                "status": "Pending"
            }

            user = users_collection.find_one({"email": email})
            # purchased = False

            # for library_item in user["library"]:
            #     if library_item["ebook"] == ebook["name"]:
            #         purchased = True
            #         break

            # if not purchased:
            users_collection.update_one(
                {"email": email},
                {
                    "$push": {
                        "pending_orders": order_entry
                    }
                }
            )

            # else:
            #     print("######## Ebook already purchased ########")
            #     return jsonify({"error": "Ebook already purchased"}), 400

            # return redirect(url_for("payment-success.PaymentSuccess"))
            return jsonify({"message": "Payment Successful"}), 200
        
        except razorpay.errors.SignatureVerificationError:
            # return redirect(url_for("payment-failed.PaymentFailed"))
            return jsonify({"error": "Payment Verification failed"}), 400
