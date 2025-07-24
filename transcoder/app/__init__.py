import os

from celery import Celery

celery = Celery(
    'transcoder',
    broker=os.environ.get("CELERY_BROKER_URL"),
    backend=os.environ.get("CELERY_RESULT_BACKEND"),
)

celery.autodiscover_tasks(['app.tasks'])
