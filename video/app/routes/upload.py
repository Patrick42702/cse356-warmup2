import os
import uuid
from datetime import datetime

import boto3
import magic
from app.db import db
from app.s3 import s3
from app.services.transcode_trigger import trigger_transcode
from app.util import error, jwt_required, success
from flask import Blueprint, g, request, logging

ALLOWED_EXTENSIONS = {"mp4", "mov"}
ALLOWED_MIME_TYPES = {"video/mp4", "video/quicktime"}

upload_bp = Blueprint("upload", __name__)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/upload", methods=["POST"])
@jwt_required
def upload_video():
    video = request.files.get("video")
    title = request.form.get("title")
    description = request.form.get("description")
    logging.logging.error(f"This is the description: {description}")
    if not video:
        return error("No file uploaded", 400)

    if not allowed_file(video.filename):
        return error("Only .mp4/mov files are allowed", 400)

    if not title:
        return error("Title is required", 400)

    if not description:
        return error("Description is required", 400)
    if len(description) > 200:
        return error("Description must be 200 characters or less", 400)

    mime = magic.from_buffer(video.read(2048), mime=True)
    video.seek(0)
    if mime not in ALLOWED_MIME_TYPES:
        return error(f"Invalid MIME type: {mime}", 400)
    video_id = str(uuid.uuid4())
    filename = f"{video_id}.mp4"
    s3_key = f"videos/{video_id}"
    s3_file = f"{s3_key}/{filename}"
    try:
        s3.upload_fileobj(video, os.environ.get("S3_BUCKET"), s3_file)
    except Exception as e:
        return error(f"S3 Upload failed. {str(e)}", 500)

    try:
        url = s3.generate_presigned_url(
            "get_object", {"Bucket": os.environ.get("S3_BUCKET"), "Key": s3_file}
        )
    except Exception as e:
        error(f"Error generating S3 URL: {str(e)}", 500)

    try:
        db["videos"].insert_one(
            {
                "video_id": video_id,
                "user_id": g.current_user["sub"],
                "filename": filename,
                "status": "uploaded",
                "title": str(title),
                "description": str(description),
                "s3_key": s3_key,
                "created_at": datetime.now(),
            }
        )
    except Exception as e:
        error(f"Error inserting video into the database: {str(e)}", 500)

    try:
        trigger_transcode(url, filename, video_id)
    except Exception as e:
        error(f"Transcoding trigger failed: {str(e)}", 500)

    return success(data={}, message="video uploaded")
