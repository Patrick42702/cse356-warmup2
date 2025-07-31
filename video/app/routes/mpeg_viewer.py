import os

from app.s3 import s3
from app.util import error, success
from flask import Blueprint, Response, logging

mpeg_player_bp = Blueprint('mpeg_player', __name__)

S3_BUCKET = os.environ.get("S3_BUCKET")

#NOTE: This route is used to retrieve mpeg-dash files for the frontend from s3
@mpeg_player_bp.route('/dash/<video_id>/<filename>', methods=['GET'])
def mpeg_player(video_id, filename):
    s3_key = f"videos/{video_id}/{filename}"

    try:
        logging.logging.error(f"this is s3_key: {s3_key}")
        res = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)
        # Stream the file content
        return Response(
            res['Body'].read(),
            mimetype=res['ContentType']
        )

    except s3.exceptions.NoSuchKey:
        return error("File not found", 404)
    except Exception as e:
        return error(f"An error occurred: {str(e)}", 500)

    return
