import os
import traceback

from app.db import db
from app.util import error, success
from bson import ObjectId
from flask import Blueprint, logging, request

VIDEO_BUCKET = os.environ.get("S3_BUCKET")

serve_bp = Blueprint('serve', __name__)

@serve_bp.route('/videos', methods=['POST'])
def get_videos(): # TODO: PAGING
    req = request.get_json()
    size = req.get("size", 10)
    size = max(size, 10) # Max serve 10 videos
    urls = []

    try:
        query = db.videos.find({"status": "processed"}).limit(size)
        for video in query:
            video_id = str(video["video_id"])
            thumbnail_filename = f"thumbnail_{video_id}.jpg"
            thumbnail_url = f"http://{os.environ.get('VIDEO_API_DOMAIN')}/api/video/dash/{video_id}/{thumbnail_filename}"
            user = db.users.find_one({"_id": ObjectId(video["user_id"])})

            urls.append({
                "video_id": video_id,
                "thumbnail_url": thumbnail_url,
                "title": video.get("title", "No title provided"),
                "user": user.get("email", "Unknown user")
            })
        return success(data={"videos": urls}, message="URL's for the mpeg-dash files")

    except Exception as e:
        traceback_str = traceback.format_exc()
        logging.logging.error("Traceback str:", traceback_str)
        return error(f"There was an error: {e}", 500)
