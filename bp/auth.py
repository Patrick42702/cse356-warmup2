from flask import Blueprint, current_app, render_template, make_response
import os
import json

from flask import request
from email_validator import validate_email
from urllib.parse import quote

import smtplib
from email.mime.text import MIMEText
from email import charset
from .util import db, error, success, validate_session, DOMAIN
from .routes import check_session
from .collaborative_filtering import rec_algo

import jwt

auth = Blueprint('auth', __name__)

@auth.route('/testmail', methods=['GET'])
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


@auth.route('/api/adduser', methods=['POST'])
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
            user_id = users.insert_one({"username": username,
                              "password": password,
                              "email": email,
                              "validated": False,
                              "videos": [],
                              "watched": [],
                              "verify-key": verify_key}).inserted_id
            rec_algo.add_user(user_id)

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


@auth.route('/api/login', methods=['POST'])
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
            access_token = jwt.encode({"username": username}, current_app.config["SECRET_KEY"], algorithm="HS256")
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

# He specifies to use query string params for the verify endpoint
@auth.route('/api/verify', methods=['GET'])
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


@auth.route('/api/logout', methods=["POST"])
@check_session
def logout():
    cookies = request.cookies
    users = db.users
    try:
        identity = jwt.decode(cookies["session_id"], current_app.config["SECRET_KEY"], algorithms=["HS256"])
        # user = users.find_one({"username": identity["username"]})
        # if "session_id" in request.cookies and validate_session(request.cookies["session_id"]):
        users.update_one({"username": identity["username"]}, {"$set": {"session_id": None, "login": False}})
        response = success({"message": "Logout successful"})
        response.delete_cookie("session_id")
        return response
        # else:
        #     raise Exception("There was an error verifying that you were already logged in")
    except Exception as e:
        return error(str(e))


@auth.route('/api/check-auth', methods=["POST"])
def check_auth():
    cookies = request.cookies
    users = db.users
    try:
        if "session_id" not in request.cookies:
            raise Exception("You do not have an active session token")
        identity = jwt.decode(cookies["session_id"], current_app.config["SECRET_KEY"], algorithms=["HS256"])
        if validate_session(cookies["session_id"]):
            user = users.find_one({"username": identity["username"]})
            return success({"isLoggedIn": user["login"], "userId": str(user["_id"])})
            raise Exception("")
    except Exception as e:
        return error(str(e))

