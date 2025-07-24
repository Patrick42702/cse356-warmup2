import datetime
import os
import uuid

import bcrypt
import jwt
from flask import jsonify


def success(data=None, message="OK"):
    return jsonify({"message": message, "data": data}), 200

def error(message="An error occurred", code=400):
    return jsonify({"error": message}), code

def generate_token(user_id):
    payload = {
        "sub": user_id,
        "jti": str(uuid.uuid4()),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
        "iat": datetime.datetime.utcnow()
    }
    return jwt.encode(payload, os.environ.get("SECRET_KEY"), algorithm="HS256")

def verify_token(token):
    return jwt.decode(token, os.environ.get("SECRET_KEY"), algorithms=["HS256"])

def hash_password(plain_password):
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
    return hashed

def check_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
