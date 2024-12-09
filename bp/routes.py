from flask import send_from_directory, request, make_response, Blueprint, render_template, current_app, g, redirect, url_for
from .util import error, success, SUBMIT_ID, validate_session, connect_db
from functools import wraps
import json
import jwt
import os
from .collaborative_filtering import rec_algo
from bson import ObjectId
from .log_util import request_loggers
routes = Blueprint('routes', __name__)
video_interaction_logger, get_videos_logger, upload_file_logger, processing_status_logger, auth_logger = request_loggers
db = connect_db()

# decorator to check if user is logged in
def check_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "token" in request.cookies and (user := validate_session(request.cookies["token"])):
            g.user = user
            return f(*args, **kwargs)
        else:
            return error("User not logged in")
    return wrapper


@routes.route('/')
def user_interface():
    try:
        if "token" in request.cookies and validate_session(request.cookies["token"]):
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
def view_video():
    try:
        user = g.user
        video_id = request.json['id']
        if video_id in user['watched']:
            return success({'viewed': True})
        else:
            db.users.update_one({'_id': user['_id']}, {'$push': {'watched': video_id}})
            return success({'viewed': False})
    except Exception as e:
        return error(str(e))

@routes.route('/api/like', methods=["POST"])
@check_session
def like_video():
    try:
        user = g.user
        video_id = request.json['id']
        value = '1' if request.json['value'] else '-1'
        like_count = rec_algo.add_like(str(user['_id']), video_id, value)
        return error("Value already set") if like_count==-1 else success({'likes': like_count})
    except Exception as e:
        return error(str(e))

@routes.route('/api/videos', methods=["POST"])
@check_session
def get_videos():
    try:
        user = g.user
        # get_videos_logger.debug(f"User liked: {[doc['_id'] for doc in db.videos.find({ 'likes': { '$elemMatch': { 'user': user['_id'] } } })]}")
        count = int(request.json["count"])
        video_id = request.json.get("videoId")
        ready_to_watch = request.json.get("readyToWatch")
        if video_id:
            if isinstance(video_id, dict): video_id = video_id['id']
            # get_videos_logger.info(f"Getting {count} recommendations for user {user['username']} ({user['_id']}) based on video {video_id}\nwatched: {user['watched']}")
            # get_videos_logger.debug(f"Video: {list(db.videos.find({'_id': ObjectId(video_id)}))}")
            recommended_video_ids, liked_list, like_counts = rec_algo.video_based_recommendations(str(user['_id']), video_id, user['watched'], count, ready_to_watch=ready_to_watch)
        else:
            # get_videos_logger.info(f"Getting {count} recommendations for user {user['username']} ({user['_id']})\nwatched: {user['watched']}")
            recommended_video_ids, liked_list, like_counts = rec_algo.user_based_recommendations(str(user['_id']), user['watched'], count, ready_to_watch=ready_to_watch)
        get_videos_logger.info(f"Recommended video ids: {recommended_video_ids}")
        recommended_videos = db.videos.find({'_id': {'$in': [ObjectId(video_id) for video_id in recommended_video_ids]}})
        videos_info = []
        for video, liked, like_count in zip(recommended_videos, liked_list, like_counts):
            video_id = str(video['_id'])
            description = video['description']
            watched = str(video['_id']) in user['watched']
            videos_info.append({'id': video_id, 'description': description, 'watched': watched, 'liked': liked, 'likevalues': like_count})
        get_videos_logger.info(f"Returning {len(videos_info)} videos")
        return success({"videos": videos_info})
    except Exception as e:
        return error(str(e))


@routes.route('/media/<path:path>', methods=["GET"])
@check_session
def get_media(path):
    id = path.split("_")[1]
    try:
        resp = make_response(send_from_directory(f"{current_app.static_folder}/media/{id}", path))
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
        user = g.user
        author = request.form["author"]
        title = request.form["title"]
        description = request.form["description"]
        video_id = videos.insert_one({"user": user["_id"], "author": author, "title": title, "description": description, "status": "processing"}).inserted_id
        rec_algo.add_video(str(video_id))
        users.update_one({"_id": user["_id"]}, {"$push": {"videos": video_id}})
        mp4file = request.files["mp4File"]
        if mp4file.filename != '':
            os.makedirs(f"{current_app.static_folder}/media/{video_id}", exist_ok=True)
            upload_file_logger.info(f"Saving video with id {video_id} in upload")
            mp4file.save(f"{current_app.static_folder}/media/{video_id}/{video_id}.mp4")
        # get the file_path of the video we receive and pass it to the celery task so it can do work
        bp_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(bp_dir)
        media_dir = os.path.join(project_root, "static", "media")
        file_name = os.path.join(media_dir, f"{video_id}", f"{video_id}.mp4")
        current_app.celery.send_task("bp.tasks.process_video", args=[file_name])
        return success({"id": str(video_id)})
    except Exception as e:
        return error("Failed to upload file")

@routes.route('/api/processing-status')
@check_session
def processing_status():
    try:
        videos = db.videos
        user = g.user
        videos = videos.find({"user": user["_id"]}, {"_id": 1, "title": 1, "status": 1})
        if videos:
            return success({"videos": [{"id": str(video["_id"]),
                                        "title": video["title"],
                                        "status": video["status"]} for video in videos]})
    except Exception as e:
        return error(str(e))

@routes.route('/api/thumbnail/<id>')
def get_thumbnail(id):
    thumbnail = current_app.static_folder + f"/media/{id}/thumbnail_{id}.jpg"

    # Verify if the file exists
    if not os.path.exists(thumbnail):
        return error("File not found")

    # Serve the file using `send_from_directory`
    resp = make_response(send_from_directory(f"{current_app.static_folder}/media/{id}", f"thumbnail_{id}.jpg"))
    resp.headers["X-CSE356"] = SUBMIT_ID
    return resp

@routes.route('/api/<path:path>', methods=["GET"])
def api_media(path):
    ftype = path.split("/")[0] #manifest
    id = path.split("/")[-1] #id
    fpath = ""
    if ftype == "manifest":
        fpath += f"{id}.mpd"
    try:
        if "token" in request.cookies and validate_session(request.cookies["token"]):
            resp = make_response(send_from_directory(f"{current_app.static_folder}/media/{id}", fpath))
            resp.headers["X-CSE356"] = SUBMIT_ID
            return resp
        else:
            raise Exception("User not logged in")
    except Exception as e:
        return error(str(e))
