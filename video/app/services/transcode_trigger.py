import os

from celery import Celery

celery = Celery(broker=os.environ.get("CELERY_BROKER_URL"))


def trigger_transcode(s3_url, file, file_id):
    return celery.send_task('transcoder.process_video', args=[s3_url, file, file_id])
