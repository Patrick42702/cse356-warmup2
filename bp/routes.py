from flask import send_from_directory, request, make_response, Blueprint, render_template, current_app, g, redirect, url_for
from .util import error, success, SUBMIT_ID, validate_session
from functools import wraps
import json
import uuid
import os

routes = Blueprint('routes', __name__)

@routes.before_request
def get_videolist():
    with open(f'{current_app.static_folder}/m1.json') as f:
        video_data = json.load(f)
    g.video_list = [{"id": title.split('-')[0], "metadata":{"title": title, "description": description}} for title, description in video_data.items()]
    return

# decorator to check if user is logged in
def check_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "session_id" in request.cookies and validate_session(request.cookies["session_id"]):
            return f(*args, **kwargs)
        else:
            return error("User not logged in")
    return wrapper


@routes.route('/')
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


@routes.route('/play/<id>', methods=['GET'])
@check_session
def play_video(id):
    try:
        resp = make_response(render_template("viewer.html"))
        resp.headers["X-CSE356"] = SUBMIT_ID
        return resp
    except Exception as e:
        return error(str(e))


@routes.route('/api/videos', methods=["POST"])
def get_videos():
    try:
        if "count" not in request.json:
            raise Exception("Count parameter not found")

        count = int(request.json["count"])
        return success({"videos": g.video_list[:count]})

    except Exception as e:
        return error(str(e))


@routes.route('/media/<path:path>', methods=["GET"])
@check_session
def get_media(path):
    try:
        resp = make_response(send_from_directory(f"{current_app.static_folder}/media", path))
        resp.headers["X-CSE356"] = SUBMIT_ID
        return resp
    except Exception as e:
        return error(str(e), weird_case='media')


@routes.route('/upload')
def upload_page():
    return render_template("upload.html")


@routes.route('/api/upload', methods=["POST"])
@check_session
def upload_file():
    try:
        author = request.form["author"]
        title = request.form["title"]
        mp4file = request.files["mp4file"]
        if mp4file.filename != '':
            mp4file.save(f"{current_app.static_folder}/media/tmp/{mp4file.filename}")
        file_id = os.urandom(10).hex()
        return redirect(url_for('routes.user_interface'))
    except Exception as e:
        return error("Failed to upload file")


@routes.route('/api/<path:path>', methods=["GET"])
def api_media(path):
    ftype = path.split("/")[0]
    file = path.split("/")[-1]
    id = file.split("-")[0]
    fpath = ""
    if ftype == "manifest":
        fpath += f"{id}.mpd"
    elif ftype == "thumbnail":
        fpath += f"thumbnail_{id}.jpg"
    try:
        if "session_id" in request.cookies and validate_session(request.cookies["session_id"]):
            resp = make_response(send_from_directory(f"{current_app.static_folder}/media", fpath))
            resp.headers["X-CSE356"] = SUBMIT_ID
            return resp
        else:
            raise Exception("User not logged in")
    except Exception as e:
        return error(str(e))
