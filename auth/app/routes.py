from app.db import db
from app.util import (
    check_password,
    error,
    generate_token,
    hash_password,
    success,
    verify_token,
)
from app.mail import send_verification_email
from flask import Blueprint, current_app, request

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return error("Missing email or password")

    email = data["email"]
    password = data["password"]

    try:
        existing_user = db.users.find_one({"email": email})
        if existing_user:
            return error("User already exists", 409)
        db.users.insert_one({"email": email, "password": hash_password(password)})
        send_verification_email(email, generate_token(email))
        return success(message="User successfully created")

    except Exception as e:
        current_app.logger.exception(f"Register error: {e}")
        return error("Internal server error", 500)


@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return error("Missing email or password", 400)

    email = data["email"]
    password = data["password"]

    try:
        user = db.users.find_one({"email": email})
        if not user or not check_password(password, user["password"]):
            return error("Invalid email or password", 401)

        # if not user.get("verified", False):
        #     return error("Email not verified", 403)
        token = generate_token(str(user["_id"]))
        return success(data={"token": token}, message="User succesfully logged in")
    except Exception as e:
        current_app.logger.exception(f"Login error: {e}")
        return error("Internal server error", 500)


@auth.route("/refresh", methods=["POST"])
def refresh_token():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return error("Missing or invalid Authorization header", 401)

    token = auth_header.split(" ")[1]
    current_app.logger.info(token)
    try:
        user_id = verify_token(token)["sub"]
        if not user_id:
            return error("Invalid or expired token", 401)

        new_token = generate_token(user_id)
        return success(data=new_token, message="Token refreshed")
    except Exception as e:
        current_app.logger.exception(f"Token refresh error: {e}")
        return error("Internal server error", 500)


@auth.route("/verify", methods=["GET"])
def verify():
    token = request.args.get("token")
    if not token:
        return error("Missing token", 400)

    try:
        email = verify_token(token)["sub"]
        if not email:
            return error("Invalid or expired token", 400)

        db.users.update_one({"email": email}, {"$set": {"verified": True}})
        return success(message="Email successfully verified")
    except Exception as e:
        current_app.logger.exception(f"Email verification error: {e}")
        return error("Internal server error", 500)
