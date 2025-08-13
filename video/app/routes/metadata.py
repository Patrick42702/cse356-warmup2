import os
import traceback

from app.db import db
from app.util import error, success
from bson import ObjectId
from flask import Blueprint, logging, request

metadata_bp = Blueprint("metadata", __name__)

@metadata_bp.route("/metadata/<video_id>", methods=["GET"])
def get_videos(video_id):  # TODO: PAGING
    if not video_id:
        return error("Video ID is required", 400)

    try:
        video = db.videos.find_one({"video_id": str(video_id)})
        if not video:
            return error("Video not found", 404)
        title = video.get("title", "No title provided")
        description = video.get("description", "No description provided")
        thumbnail_url = f"http://localhost/api/video/dash/{video_id}/thumbnail_{video_id}.jpg"
        return success(data={"metadata": {
            "title": title,
            "description": description,
            "thumbnail_url": thumbnail_url,
        }
        }, message="Video metadata retrieved successfully")

    except Exception as e:
        traceback_str = traceback.format_exc()
        logging.logging.error("Traceback str:", traceback_str)
        return error(f"There was an error: {e}", 500)
