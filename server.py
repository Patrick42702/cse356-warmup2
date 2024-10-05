import os
from flask import Flask, jsonify, request, make_response
from pymongo import MongoClient
from email_validator import validate_email
from flask_mail import Mail, Message

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

DOMAIN = "esk-pj-airplanes.cse356.compas.cs.stonybrook.edu"
SUBMIT_ID = "66d216517f77bf55c5005074"

# configure flask app and pymongo
app = Flask(__name__)
client = MongoClient("localhost", 27017)
db = client.eskpj_airplanes

#config env variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# configure mail server
# our DNS is esk-pj-airplanes.cse357.compas.cs.stonybrook.edu
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 25
app.config['MAIL_DEFAULT_SENDER'] = f"root@{DOMAIN}"
mail = Mail(app)

# configure JWTManager
jwt = JWTManager(app)
app.config['JWT_BLACKLIST_ENABLED'] = True

# error handling
def error(err_msg):
    return jsonify({"status": "ERROR", "error":True, "message": err_msg}), 200

# valid reponse handling
def success(data, session_id=None):
    # assume data is a dictioanry
    data["status"] = "OK"
    response = make_response(jsonify(data))
    if session_id:
        response.set_cookie("session_id", session_id)
        response.headers["Authorization"] = f"Bearer {session_id}"
    response.headers["X-CSE356"] = SUBMIT_ID
    return response

# validate session
def validate_session(user, session_id):
    if user["session_id"] == session_id:
        return True
    else:
        return False

# for now get params via a POST form. Adjust when we have an answer
# from ferdman on how to get params
@app.route('/adduser', methods=['POST'])
def add_user():
    users = db.users
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    try:
        if username and password and validate_email(email):
            existing_user = users.find_one({"username": username})
            existing_email = users.find_one({"email": email})
            if existing_user or existing_email:
                raise Exception("User or email already exists")
            verify_key = create_access_token(identity=email, expires_delta=False)
            users.insert_one({"username": username,
                              "password": password,
                              "email": email,
                              "validated": False,
                              "verify-key": verify_key})
            # msg = Message(subject="Verify email",
            #               recipients=[email],
            #               body=f"Please verify your email at http://{DOMAIN}?email={email}&?verify={verify_key}")
            # mail.send(msg)
        return success({"message": "User successfully added"})
    except Exception as e:
        return error(str(e))

# He specifies to use query string params for the verify endpoint
@app.route('/verify', methods=['GET'])
def verify():
    users = db.users
    email = request.args["email"]
    verify_key = request.args["verify"]
    try:
        user = users.find_one({"email": email})
        saved_token = user["verify-key"]
        if saved_token == verify_key:
            users.update_one({"email": email}, {"$set": {"validated": True}})
            return success({"message" : "Email Successfully Verified"})
        else:
            raise Exception("Invalid verification key")
        return
    except Exception as e:
        return error(str(e))

@app.route('/login', methods=['POST'])
def login():
    users = db.users
    username = request.json['username']
    password = request.json['password']
    try:
        if username and password and users.find_one({"username": username}):
            user = users.find_one({"username": username})
        else:
            raise Exception("username not found")
        if user["password"] == password and user["validated"]:
            success_msg = {"message" :"Login successful"}
            access_token = create_access_token(identity=username)
            users.update_one({"username": username}, {"$set": {"session_id": access_token}})
            return success(success_msg, access_token)
        else:
            if user["password"] != password:
                raise Exception("Invalid password")
            else:
                raise Exception("User not validated")
    except Exception as e:
        print(e)
        return error(str(e))

@jwt.expired_token_loader
def expired_token_response(jwt_header, jwt_payload):
    return error("Token has expired")

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    blacklist = db.blacklist
    jti = jwt_payload["jti"]
    return jti in blacklist

@app.route('/logout', methods=["POST"])
@jwt_required()
def logout():
    # cookies = request.cookies
    users = db.users
    identity = get_jwt_identity()
    user = users.find_one({"username": identity})
    print(user)
    try:
        if validate_session(user, user["session_id"]):
            print("valid session")
            users.update_one({"username": identity}, {"$set": {"session_id": None}})
            return success({"message": "Logout successful"})
        else:
            raise Exception("There was an error verifying that you were already logged in")
    except Exception as e:
        return error(str(e))
