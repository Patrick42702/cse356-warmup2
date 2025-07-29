import os
import uuid
from datetime import datetime

import boto3
import magic
from app.db import db
from app.services.transcode_trigger import trigger_transcode
from app.util import error, success
from flask import Blueprint, request

ALLOWED_EXTENSIONS = {'mp4'}
ALLOWED_MIME_TYPES = {'video/mp4'}

upload_bp = Blueprint('upload', __name__)
session = boto3.session.Session()

s3 = session.client(
    's3',
    endpoint_url=os.environ.get("S3_ENDPOINT"),
    aws_access_key_id=os.environ.get("S3_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("S3_SECRET_KEY")
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload', methods=['POST'])
def upload_video():
    video = request.files.get('video')
    if not video:
        return error("No file uploaded", 400)

    if not allowed_file(video.filename):
        return error("Only .mp4 files are allowed", 400)

    mime = magic.from_buffer(video.read(2048), mime=True)
    video.seek(0)
    if mime not in ALLOWED_MIME_TYPES:
        return error(f"Invalid MIME type: {mime}", 400)
    video_id = uuid.uuid4()
    filename = f"{video_id}.mp4"
    s3_key = f"videos/{video_id}/{filename}"
    try:
        s3.upload_fileobj(video, "video-bucket", s3_key)
    except Exception as e:
        return error(f"S3 Upload failed. {str(e)}", 500)

    url = s3.generate_presigned_url("get_object", {
        "Bucket": "video-bucket",
        "Key": s3_key
    })

    db["videos"].insert_one({
        "video_id": str(video_id),
        "filename": filename,
        "uploader_id": "user", # TODO
        "status": "uploaded",
        "s3_key": s3_key,
        "created_at": datetime.now()
    })

    trigger_transcode(url, filename, video_id)

    return success(data={"url": url}, message="video uploaded")

