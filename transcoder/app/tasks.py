from . import celery
from .db import get_mongo_client
from .util import transcode_to_mpeg_dash


@celery.task(name="transcoder.process_video")
def process_video(s3_url, file, file_id):
    db = get_mongo_client()
    transcode_to_mpeg_dash(s3_url, file, file_id, db)
