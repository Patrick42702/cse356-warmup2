from flask import send_from_directory, request, make_response, Blueprint, render_template, current_app, g, redirect, url_for
from .util import error, success, SUBMIT_ID, validate_session, connect_db, get_user
from functools import wraps
import json
import jwt
import os
from .collaborative_filtering import rec_algo
routes = Blueprint('routes', __name__)

db = connect_db()

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

@routes.route('/api/view', methods=["POST"])
@check_session
def view_video_like():
    try:
        user = get_user(request.cookies)
        video_id = request.form['id']
        if video_id in user['watched']:
            return success({'viewed': True})
        else:
            db.users.update_one({'_id': video_id}, {'$push': {'watched': video_id}})
            return success({'viewed': False})
    except Exception as e:
        return error(str(e))

@routes.route('/api/like', methods=["POST"])
@check_session
def view_video():
    try:
        user = get_user(request.cookies)
        video_id = request.form['id']
        value = 1 if request.form['value'] else -1
        likes = db.videos.find_one({'_id': video_id})['likes']
        likecount = sum(1 for like in likes if like['value']==1)
        like = next((like for like in likes if like['user'] == user['_id']), None)
        if like:
            if like['value'] == value: return error("Video already liked") if value == 1 else error("Video already disliked")
            db.videos.update_one({'_id': video_id, 'likes.user': like['user']}, {'$set': {'likes.$.value': value}})
            likecount += value
        else:
            db.videos.update_one({'_id': video_id}, {'$push': {'likes': {'user': user['_id'], 'value': value}}})
            if value == 1: likecount += 1
        return success({'likes': likecount})
    except Exception as e:
        return error(str(e))

@routes.route('/api/videos', methods=["POST"])
def get_videos():
    try:
        user = get_user(request.cookies)
        count = int(request.json["count"])
        recommended_video_ids = rec_algo.get_top_recommendations(user['_id'], user['watched'], count)
        recommended_videos = db.videos.find({'_id': {'$in': recommended_video_ids}})
        videos_info = []
        for video in recommended_videos:
            video_id = video['_id']
            description = 'A video'
            watched = video['_id'] in user['watched']
            liked = next((like == 1 for like in video['likes'] if like['user'] == user['_id']), None)
            likevalues = sum(1 for like in video['likes'] if like['value']==1)
            videos_info.append({'id': video_id, 'description': description, 'watched': watched, 'liked': liked, 'likevalues': likevalues})
        return success({"videos": videos_info})
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
        return error(str(e))


@routes.route('/upload')
def upload_page():
    return render_template("upload.html")


@routes.route('/api/upload', methods=["POST"])
@check_session
def upload_file():
    try:
        users = db.users
        videos = db.videos
        user = get_user(request.cookies)
        author = request.form["author"]
        title = request.form["title"]
        video_id = videos.insert_one({"user": user["_id"], "author": author, "title": title, "status": "processing", "likes": []}).inserted_id
        rec_algo.add_video(video_id)
        users.update_one({"_id": user["_id"]}, {"$push": {"videos": video_id}})
        mp4file = request.files["mp4file"]
        if mp4file.filename != '':
            os.makedirs(f"{current_app.static_folder}/tmp/{video_id}", exist_ok=True)
            mp4file.save(f"{current_app.static_folder}/tmp/{video_id}/{video_id}.mp4")
        # get the file_path of the video we receive and pass it to the celery task so it can do work
        bp_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(bp_dir)
        tmp_dir = os.path.join(project_root, "static", "tmp")
        file_name = os.path.join(tmp_dir, f"{video_id}", f"{video_id}.mp4")
        current_app.celery.send_task("bp.tasks.process_video", args=[file_name])
        return success({"id": str(video_id)})
    except Exception as e:
        return error("Failed to upload file")

@routes.route('/api/processing-status')
@check_session
def processing_status():
    try:
        videos = db.videos
        user = get_user(request.cookies)
        videos = videos.find({"user": user["_id"]}, {"_id": 1, "title": 1, "status": 1})
        if videos:
            return success({"videos": [{"id": str(video["_id"]),
                                        "title": video["title"],
                                        "status": video["status"]} for video in videos]})
    except Exception as e:
        return error(str(e))


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