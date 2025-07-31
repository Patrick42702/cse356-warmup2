import os
import traceback

from app.db import db
from app.s3 import s3
from app.util import error, success
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
            mpd_key = f"videos/{video_id}/{video_id}.mpd"
            thumbnail_key = f"videos/{video_id}/thumbnail_{video_id}.jpg"

            mpd_url = s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": VIDEO_BUCKET,
                    "Key": mpd_key
                },
                ExpiresIn=3600 # 1 hour
            )

            thumbnail_url = s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": VIDEO_BUCKET,
                    "Key": thumbnail_key
                },
                ExpiresIn=3600 # 1 hour
            )

            urls.append({
                "video_id": video_id,
                "mpd_url": mpd_url,
                "thumbnail_url": thumbnail_url
            })
        return success(data={"videos": urls}, message="URL's for the mpeg-dash files")

    except Exception as e:
        traceback_str = traceback.format_exc()
        logging.logging.error("Traceback str:", traceback_str)
        return error(f"There was an error: {e}", 500)
