import os
from flask import Flask, jsonify, request
from pymongo import MongoClient
from email_validator import validate_email
from flask_mail import Mail, Message

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

DOMAIN = "esk-pj-airplanes.cse356.compas.cs.stonybrook.edu"

# configure flask app and pymongo
app = Flask(__name__)
client = MongoClient("localhost", 27017)
db = client.eskpj_airplanes

#config env variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# configure mail server
# our DNS is esk-pj-airplanes.cse356.compas.cs.stonybrook.edu
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 25
app.config['MAIL_DEFAULT_SENDER'] = f"root@{DOMAIN}"
mail = Mail(app)

# configure JWTManager
jwt = JWTManager(app)

# example route that contacts database. Users is a collection in the eskpj_airplanes database
@app.route('/data')
def get_data():
    users = db.users
    data = users.find_one({"name": "patrick"})
    result = [{"_id": str(item[0]), "name": str(item[1])} for item in data.items()]
    print(result)
    return jsonify(result)

# for now get params via a POST form. Adjust when we have an answer
# from ferdman on how to get params
@app.route('/adduser', methods=['POST'])
def add_user():
    users = db.users
    print(request.json)
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    try:
        if username and password and validate_email(email):
            existing_user = users.find_one({"email": email})
            if existing_user:
                raise Exception("User already exists")
            verify_key = create_access_token(identity=email)
            users.insert_one({"username": username,
                              "password": password,
                              "email": email,
                              "validated": False,
                              "verify-key": verify_key})
            print(f"this is my verify key {verify_key}")
            msg = Message(subject="Verify email", 
                          recipients=[email], 
                          body=f"Please verify your email at http://{DOMAIN}?email={email}&?verify={verify_key}")
            mail.send(msg)
        return "User added successfully. Please verify email"
    except Exception as e:
        return jsonify(str(e.args[0])), 400

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
            return jsonify("Email Successfully Verified")
        else:
            raise Exception("Invalid verification key")
        return
    except Exception as e:
        return jsonify(str(e.args[0])), 400

@app.route('/login', methods=['POST'])
def login():
    users = db.users
    try:
        if request.form['username'] and request.form['password']:
            users.insert_one({"username": request.form['username'],
                              "password": request.form['password']})

        return "User added"
    except Exception as e:
        return e

@app.route('/logout')
def logout():
    return "Logout"
