import os
import quopri
import traceback

from flask import Flask, jsonify, request, make_response, render_template, send_from_directory
from pymongo import MongoClient
from email_validator import validate_email
from flask_mail import Mail, Message
from urllib.parse import quote
from email.message import EmailMessage

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import charset

# from flask_jwt_extended import create_access_token
# from flask_jwt_extended import get_jwt_identity
# from flask_jwt_extended import jwt_required
# from flask_jwt_extended import JWTManager

import jwt

DOMAIN = "esk-pj-airplanes.cse356.compas.cs.stonybrook.edu"
SUBMIT_ID = "66d216517f77bf55c5005074"

# configure flask app and pymongo
app = Flask(__name__)
client = MongoClient("localhost", 27017)
db = client.eskpj_airplanes

#config env variables
os.environ['SECRET_KEY'] = os.urandom(12).hex()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# configure mail server
# our DNS is esk-pj-airplanes.cse357.compas.cs.stonybrook.edu
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 25
app.config['MAIL_DEFAULT_SENDER'] = f"root@{DOMAIN}"
mail = Mail(app)

# configure JWTManager
# jwt = JWTManager(app)
# app.config['JWT_BLACKLIST_ENABLED'] = True

# error handling
def error(err_msg, weird_case=None):
    print(f"found an error: {err_msg}")
    traceback.print_exc()
    resp = make_response(jsonify({"status": "ERROR", "error":True, "message": err_msg}), 200)
    if weird_case == "media":
        resp = make_response('{"status":"ERROR","error":True,"message":"error"}', 200) # more silly spaces?
    resp.headers["X-CSE356"] = SUBMIT_ID
    return resp

# valid reponse handling
def success(data, session_id=None):
    # assume data is a dictioanry
    data["status"] = "OK"
    # response = make_response(jsonify(data))
    response = make_response('{"status":"OK"}') # try setting it directly to remove spaces and such
    if session_id:
        response.set_cookie("session_id", session_id)
    response.headers["X-CSE356"] = SUBMIT_ID
    return response

# validate session
def validate_session(session_id):
    identity = jwt.decode(session_id, app.config['SECRET_KEY'], algorithms=["HS256"])
    email = identity["username"]
    user = db.users.find_one({"username": email})
    if user["session_id"] == request.cookies["session_id"]:
        return True
    else:
        return False

@app.route('/')
def user_interface():
    try:
        if "session_id" in request.cookies and validate_session(request.cookies["session_id"]):
            resp = make_response(render_template("homepage.html"))
            resp.headers["X-CSE356"] = SUBMIT_ID
            return resp
        else:
            raise Exception("User not logged in")
    except Exception as e:
        return error(str(e))

@app.route('/testmail', methods=['GET'])
def testmail():
    try:
        email = request.args["email"]
        print(email + '\n')
        from_addr = "root@esk-pj-airplanes.cse356.compas.cs.stonybrook.edu"
        to_addr = email
        verify_key = os.urandom(12).hex()
        body = f"http://{DOMAIN}/verify?email={quote(email)}&key={verify_key}"
        cs = charset.Charset('utf-8')
        cs.body_encoding = charset.QP
        msg = MIMEText(body, 'plain', cs)
        print(msg.as_string())
        s = smtplib.SMTP('localhost', 25)
        s.sendmail(from_addr, to_addr, msg.as_string())
        s.quit()
        return success({})
    except Exception as e:
        return error(str(e))

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
            # verify_key = create_access_token(identity=email, expires_delta=False)
            verify_key = os.urandom(12).hex()
            users.insert_one({"username": username,
                              "password": password,
                              "email": email,
                              "validated": False,
                              "verify-key": verify_key})

            cs = charset.Charset('utf-8')
            cs.body_encoding = charset.QP
            from_addr = "root@esk-pj-airplanes.cse356.compas.cs.stonybrook.edu"
            to_addr = email
            body = f"http://{DOMAIN}/verify?email={quote(email)}&key={verify_key}"

            msg = MIMEText(body, 'plain', cs)
            print(msg.as_string())
            s = smtplib.SMTP('localhost', 25)
            s.sendmail(from_addr, to_addr, msg.as_string())
            s.quit()
            return success({'message': "Email sent"})

            # msg = Message(subject="Verify email",
            #               recipients=[email])
            # msg.body = f"http://{DOMAIN}/verify?email={quote(email)}&key={verify_key}"
            # mail.send(msg)

            # email_msg = EmailMessage()
            # email_msg["To"] = [email]
            # email_msg["Subject"] = "verify email"
            # email_msg.set_content(f"http://{DOMAIN}/verify?email={quote(email)}&key={verify_key}")
            # with mail.connect() as conn:
            #     conn.send_message(email_msg)
        return success({"message": "User successfully added"})
    except Exception as e:
        return error(str(e))

# He specifies to use query string params for the verify endpoint
@app.route('/verify', methods=['GET'])
def verify():
    users = db.users
    try:
        email = request.args["email"]
        verify_key = request.args["key"]
        user = users.find_one({"email": email})
        saved_token = user["verify-key"]
        if saved_token == verify_key:
            users.update_one({"email": email}, {"$set": {"validated": True}})
            return success({})
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
            # access_token = create_access_token(identity=username)
            access_token = jwt.encode({"username": username}, app.config['SECRET_KEY'], algorithm="HS256")
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

# @jwt.expired_token_loader
# def expired_token_response(jwt_header, jwt_payload):
#     return error("Token has expired")
#
# @jwt.token_in_blocklist_loader
# def check_if_token_in_blocklist(jwt_header, jwt_payload):
#     blacklist = db.blacklist.find()
#     jti = jwt_payload["jti"]
#     return jti in blacklist

@app.route('/logout', methods=["POST"])
def logout():
    cookies = request.cookies
    users = db.users
    identity = jwt.decode(cookies["session_id"], app.config['SECRET_KEY'], algorithms=["HS256"])
    user = users.find_one({"username": identity["username"]})
    try:
        if validate_session(user, user["session_id"]):
            print("valid session")
            users.update_one({"username": identity}, {"$set": {"session_id": None}})
            response = success({"message": "Logout successful"})
            response.delete_cookie("session_id")
            return response
        else:
            raise Exception("There was an error verifying that you were already logged in")
    except Exception as e:
        return error(str(e))

@app.route('/media/<path:path>', methods=["GET"])
def get_media(path):
    try:
        if "session_id" in request.cookies and validate_session(request.cookies["session_id"]):
            resp = make_response(send_from_directory("static/media", path))
            resp.headers["X-CSE356"] = SUBMIT_ID
            return resp
        else:
            raise Exception("User not logged in")
    except Exception as e:
        return error(str(e), weird_case='media')
