import os
from flask import Flask, jsonify, request, make_response, render_template, url_for, redirect
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
# our DNS is esk-pj-airplanes.cse356.compas.cs.stonybrook.edu
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 25
app.config['MAIL_DEFAULT_SENDER'] = f"root@{DOMAIN}"
mail = Mail(app)

# configure JWTManager
jwt = JWTManager(app)

# for now get params via a POST form. Adjust when we have an answer
# from ferdman on how to get params
@app.route('/adduser', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        users = db.users
        username = request.json['username']
        password = request.json['password']
        email = request.json['email']
        try:
            if username and password and validate_email(email):
                existing_user = users.find_one({"username": username})
                if existing_user:
                    raise Exception("User already exists")
                verify_key = create_access_token(identity=email)
                users.insert_one({"username": username,
                                  "password": password,
                                  "email": email,
                                  "validated": False,
                                  "verify-key": verify_key})
                msg = Message(subject="Verify email", 
                              recipients=[email], 
                              body=f"Please verify your email at http://{DOMAIN}?email={email}&?verify={verify_key}")
                mail.send(msg)
            return "User added successfully. Please verify email"
        except Exception as e:
            return jsonify(str(e.args[0])), 400
    return render_template("adduser.html")

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

@app.route('/please_verify', methods=['GET'])
def please_verify():
    return render_template("verify.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = db.users
        username = request.json['username']
        password = request.json['password']
        try:
            if username and password:
                user = users.find_one({"username": username})
            else:
                raise Exception("username not found")
            if user["password"] == password:
                # response = make_response(render_template("verify.html"))
                print("inputted correct password")
                response = make_response(redirect(url_for("please_verify")))
                access_token = create_access_token(identity=username)
                response.set_cookie("session_id", access_token)
                response.headers["X-CSE356"] = SUBMIT_ID
                print(response.response)
                return response
            else:
                raise Exception("Invalid password")
        except Exception as e:
            return jsonify(str(e.args[0])), 400
    return render_template("login.html")

@app.route('/logout')
def logout():
    return "Logout"
