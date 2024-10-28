import os
import quopri
import traceback
import json

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

# error handling
def error(err_msg, weird_case=None):
    print(f"found an error: {err_msg}")
    traceback.print_exc()
    resp = json.dumps({"status":"ERROR","error":True,"message": err_msg}), 200, {'Content-Type': 'application/json', 'X-CSE356': SUBMIT_ID}
    return resp

# valid reponse handling
def success(data, session_id=None):
    # assume data is a dictioanry
    data["status"]="OK"
    body = json.dumps(data, separators=(',', ':'))
    response = make_response(body) # try setting it directly to remove spaces and such
    if session_id:
        response.set_cookie("session_id", session_id)
    response.headers["X-CSE356"] = SUBMIT_ID
    return response

# validate session
def validate_session(session_id):
    identity = jwt.decode(session_id, app.config['SECRET_KEY'], algorithms=["HS256"])
    username = identity["username"]
    user = db.users.find_one({"username": username})
    if user["session_id"] == request.cookies["session_id"]:
        return True
    else:
        return False

@app.before_request
def log_request_info():
    app.logger.debug("-"*110)
    app.logger.debug('--- REQUEST --- ')
    app.logger.debug('Body: %s', request.get_data())
    app.logger.debug('Cookies: %s', request.cookies)

@app.after_request
def log_response(response):
    try:
        app.logger.debug('--- RESPONSE --- ')
        app.logger.debug('Status: %s', response.status)
        app.logger.debug('Cookies set: %s', response.headers.getlist("Set-Cookie"))
        app.logger.debug('Body: %s', response.get_data())
    except Exception as e:
        app.logger.debug("Can't display response.")
    app.logger.debug("-" * 110)
    return response

@app.route('/')
def user_interface():
    try:
        if "session_id" in request.cookies and validate_session(request.cookies["session_id"]):
            resp = make_response(render_template("homepage.html"))
            resp.headers["X-CSE356"] = SUBMIT_ID
            return resp
        else:
            resp = make_response(render_template("index.html"))
            resp.headers["X-CSE356"] = SUBMIT_ID
            return resp
            # raise Exception("User not logged in")
    except Exception as e:
        return error(str(e))

@app.route('/play/<id>', methods=['GET'])
def play_video(id):
    try:
        if "session_id" in request.cookies and validate_session(request.cookies["session_id"]):
            resp = make_response(render_template("viewer.html"))
            resp.headers["X-CSE356"] = SUBMIT_ID
            return resp
        else: raise Exception("User not logged in")
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
@app.route('/api/adduser', methods=['POST'])
def add_user():
    users = db.users
    try:
        username = request.json['username']
        password = request.json['password']
        email = request.json['email']
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
            body = f"Please verify your email for eskpj-airplanes video viewer at the following link: http://{DOMAIN}/api/verify?email={quote(email)}&key={verify_key}"

            msg = MIMEText(body, 'plain', cs)
            msg['Subject'] = "Verify your email with ESKPJ"
            print(msg.as_string())
            s = smtplib.SMTP('localhost', 25)
            s.sendmail(from_addr, to_addr, msg.as_string())
            s.quit()
            return success({'message': "Email sent"})
        return success({"message": "User successfully added"})
    except Exception as e:
        return error(str(e))

# He specifies to use query string params for the verify endpoint
@app.route('/api/verify', methods=['GET'])
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

@app.route('/api/login', methods=['POST'])
def login():
    users = db.users
    try:
        username = request.json['username']
        password = request.json['password']
        if username and password and users.find_one({"username": username}):
            user = users.find_one({"username": username})
        else:
            raise Exception("username not found")
        if user["password"] == password and user["validated"]:
            success_msg = {"message" :"Login successful"}
            # access_token = create_access_token(identity=username)
            access_token = jwt.encode({"username": username}, app.config['SECRET_KEY'], algorithm="HS256")
            users.update_one({"username": username}, {"$set": {"session_id": access_token, "login": True}})
            return success(success_msg, access_token)
        else:
            if user["password"] != password:
                raise Exception("Invalid password")
            else:
                raise Exception("User not validated")
    except Exception as e:
        print(e)
        return error(str(e))

@app.route('/api/logout', methods=["POST"])
def logout():
    cookies = request.cookies
    users = db.users
    try:
        identity = jwt.decode(cookies["session_id"], app.config['SECRET_KEY'], algorithms=["HS256"])
        # user = users.find_one({"username": identity["username"]})
        if "session_id" in request.cookies and validate_session(request.cookies["session_id"]):
            users.update_one({"username": identity["username"]}, {"$set": {"session_id": None, "login": False}})
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

@app.route('/api/check-auth', methods=["POST"])
def check_auth():
    cookies = request.cookies
    users = db.users
    try:
        if "session_id" not in request.cookies:
            raise Exception("You do not have an active session token")
        identity = jwt.decode(cookies["session_id"], app.config['SECRET_KEY'], algorithms=["HS256"])
        if validate_session(cookies["session_id"]):
            user = users.find_one({"username": identity["username"]})
            return success({"isLoggedIn": user["login"], "userId": str(user["_id"])})
            raise Exception("")
    except Exception as e:
        return error(str(e))

@app.route('/api/videos', methods=["POST"])
def get_videos():
    try:
        if "count" not in request.json:
            raise Exception("Count parameter not found")

        with open("static/videos/m1.json") as f:
            meta = json.load(f)
            count = request.json["count"]
            ids = list(meta.keys())
            id = ids[count - 1]
            desc = meta[id]
            return success({"title": id, "description": desc})

    except Exception as e:
        return error(str(e))











