from . import celery
from .util import transcode_to_mpeg_dash


@celery.task(name="transcoder.process_video")
def process_video(s3_url, file, file_id):
    transcode_to_mpeg_dash(s3_url, file, file_id)
