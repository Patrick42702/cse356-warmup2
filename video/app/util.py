import os
from functools import wraps

import jwt
from flask import g, jsonify, request

SECRET_KEY = os.environ.get("SECRET_KEY")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")

def success(data=None, message="OK"):
    return jsonify({"message": message, "data": data}), 200

def error(message="An error occurred", code=400):
    return jsonify({"error": message}), code

def decode_token(token: str):
    try:
        payload = jwt.decode(
            token,
            key=os.environ["SECRET_KEY"],
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired. Please login")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization header missing or invalid"}), 401

        token = auth_header.split("Bearer ")[1].strip()

        try:
            user_data = decode_token(token)
            # Save user info to Flask's global context
            g.current_user = user_data
        except ValueError as e:
            return jsonify({"error": str(e)}), 401

        return f(*args, **kwargs)
    return decorated_function
