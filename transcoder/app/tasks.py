from . import celery
from .util import transcode_to_mpeg_dash


@celery.task
def process_video(input_path, output_dir):
    transcode_to_mpeg_dash(input_path, output_dir)
