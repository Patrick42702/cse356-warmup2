import datetime
import os
import uuid

import bcrypt
import jwt
from flask import jsonify

SECRET_KEY = os.environ.get("SECRET_KEY")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")


def success(data=None, message="OK"):
    return jsonify({"message": message, "data": data}), 200


def error(message="An error occurred", code=400):
    return jsonify({"error": message}), code


def generate_token(user_id):
    payload = {
        "sub": user_id,
        "jti": str(uuid.uuid4()),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=1440),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])


def hash_password(plain_password):
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed


def check_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)
