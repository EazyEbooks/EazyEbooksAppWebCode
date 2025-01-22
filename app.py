from datetime import timedelta, datetime, timezone
from flask import Flask, session, jsonify, request, redirect, url_for, flash, current_app
from flask_smorest import Api
from pymongo import MongoClient
from resources.database.home import blp as HomeBlueprint
from resources.database.login import blp as LoginBlueprint
from resources.database.book_viewer import blp as BookViewerBlueprint
from resources.database.registration import blp as RegistrationBlueprint
from resources.database.forgot_password import blp as ForgotPasswordBlueprint
from resources.database.fp_link_sent import blp as FpLinkSentBlueprint
from resources.database.password_reset_link import blp as PasswordResetLinkBlueprint
from resources.database.profile_settings import blp as ProfileSettingsBlueprint
from resources.database.purchase_history import blp as PurchaseHistoryBlueprint
from resources.database.user_order import blp as UserOrderBlueprint
from resources.general.marketplace import blp as MarketplaceBlueprint
from resources.database.payment_success import blp as PaymentSuccessBlueprint
from resources.database.payment_failed import blp as PaymentFailedBlueprint
from resources.database.verification import blp as VerificationBlueprint

def factory_pattern(db_url=None):
    app = Flask(__name__)

    # Flask app configuration
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "GUNI CTF"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["JWT_SECRET_KEY"] = "189063608319052126134504268958895715337"
    app.secret_key = "00ae1987adf41f0d2c421f912e7eecb8e8bdc0d6fc0bb3295b1db934d1b086a4"
    app.config["EBOOK_IMAGE_UPLOAD_FOLDER"] = "static/images/books"

    # MongoDB Client
    client = MongoClient(db_url or "mongodb://localhost:27017/")
    db = client["your_database_name"]
    users_collection = db["users"]

    api = Api(app)

    # Registering all blueprints
    api.register_blueprint(HomeBlueprint)
    api.register_blueprint(LoginBlueprint)
    api.register_blueprint(BookViewerBlueprint)
    api.register_blueprint(RegistrationBlueprint)
    api.register_blueprint(ForgotPasswordBlueprint)
    api.register_blueprint(FpLinkSentBlueprint)
    api.register_blueprint(PasswordResetLinkBlueprint)
    api.register_blueprint(ProfileSettingsBlueprint)
    api.register_blueprint(PurchaseHistoryBlueprint)
    api.register_blueprint(UserOrderBlueprint)
    api.register_blueprint(MarketplaceBlueprint)
    api.register_blueprint(PaymentSuccessBlueprint)
    api.register_blueprint(PaymentFailedBlueprint)
    api.register_blueprint(VerificationBlueprint)

    @app.before_request
    def make_session_permanent():
        """
        Ensures the session is permanent.
        """
        session.permanent = True
        session.modified = True  # Mark session as updated

    return app

if __name__ == "__main__":
    factory_pattern().run(debug=True, host='0.0.0.0', port=8080)
