from server import celery
from .util import connect_db
import subprocess
import os
from bson import ObjectId
from .log_util import celery_logger

@celery.task
def process_video(filepath):
    # Video filter for padding to 16:9 aspect ratio
    scale_filter = "scale='if(gt(a,16/9),1280,-2)':'if(gt(a,16/9),-2,720)',pad=1280:720:(ow-iw)/2:(oh-ih)/2:black"

    # FFmpeg resolution and bitrate options
    ffmpeg_options = [
        ('512k', '640x360'),
        ('768k', '960x540'),
        ('1024k', '1280x720')
    ]

    # DASH options
    dash_options = [
        '-use_template', '1',
        '-use_timeline', '1',
        '-seg_duration', '10',
        '-adaptation_sets', 'id=0,streams=v',
        '-f', 'dash'
    ]
    # /Users/patrickmuller/school/sb356/cse356-warmup2/static/tmp/6728f0dd8289003926090026/6728f0dd8289003926090026.mp4
    cwd = os.path.dirname(filepath)
    os.chdir(cwd)

    filename = filepath.split('/')[-1]
    file_id = filename.split('.')[0]
    output_mpd = f"{file_id}.mpd"
    input_path = os.path.join(cwd, filename)
    celery_logger(f"{filename} is the filename, {input_path} is the input path, and {file_id} is the file id")


    # Start constructing the FFmpeg command
    ffmpeg_cmd = [
        'ffmpeg','-hide_banner', '-loglevel', 'error', '-y', '-i', input_path,
        '-vf', scale_filter, '-report'
    ]

    # Add video bitrates and resolutions
    for i, (bitrate, resolution) in enumerate(ffmpeg_options):
        ffmpeg_cmd.extend([
            '-map', '0:v',
            f'-b:v:{i}', bitrate,
            f'-s:v:{i}', resolution
        ])

    # Set segment names with video_id
    ffmpeg_cmd.extend([
        '-init_seg_name', f"init_{file_id}_$RepresentationID$.mp4",
        '-media_seg_name', f"chunk_{file_id}_$Bandwidth$_$Number$.m4s"
    ])

    # Add DASH options and output MPD file path
    ffmpeg_cmd.extend(dash_options)
    ffmpeg_cmd.append(output_mpd)

    # Run the FFmpeg command for DASH
    celery_logger(f"Processing {filename} with video ID {file_id}")
    subprocess.run(ffmpeg_cmd)

    # Generate thumbnail
    scale_thumbnails = "scale='if(gt(a,16/9),320,-2)':'if(gt(a,16/9),-2,180)',pad=320:180:(ow-iw)/2:(oh-ih)/2:black"
    thumbnail_path = f"thumbnail_{file_id}.jpg"
    thumbnail_cmd = [
        'ffmpeg','-hide_banner', '-loglevel', 'error', '-y', '-i', input_path,
        '-vf', scale_thumbnails, '-vframes', '1', thumbnail_path
    ]
    celery_logger(f"Generating thumbnail for {filename} with video ID {file_id}")
    subprocess.run(thumbnail_cmd)

    celery_logger(f"Processing complete. [{file_id}]")
    db = connect_db()
    db.videos.update_one({"_id": ObjectId(file_id)}, {"$set": {"status": "complete"}})
    return filepath

@celery.task
def save_video(filepath, video):
    video.save(filepath)
    return filepath
