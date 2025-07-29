import os
import subprocess

import boto3
import requests

TEMP_VIDEO_DIRECTORY = os.environ.get("TEMP_VIDEO_DIRECTORY")
S3_BUCKET = os.environ.get("S3_BUCKET")

session = boto3.session.Session()

s3 = session.client(
    's3',
    endpoint_url=os.environ.get("S3_ENDPOINT"),
    aws_access_key_id=os.environ.get("S3_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("S3_SECRET_KEY")
)

def upload_directory(local_dir, bucket, prefix):
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            full_path = os.path.join(root, file)
            # relative_path = os.path.relpath(full_path, local_dir)
            s3_key = f"{prefix}/{file}"
            print(f"Uploading file: {file}")
            s3.upload_file(full_path, bucket, s3_key)

def transcode_to_mpeg_dash(s3_url, file, file_id):
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

    output_path = f"{TEMP_VIDEO_DIRECTORY}/{file_id}"
    output_file = os.path.join(output_path, file)
    os.mkdir(output_path)
    os.chdir(output_path)
    req = requests.get(s3_url, stream=True)
    if req.status_code == 200:
        with open(output_file, 'wb') as f:
            for chunk in req.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded to: {output_path}")
    else:
        print(f"Failed to download file: HTTP {req.status_code}")

    # Start constructing the FFmpeg command
    ffmpeg_cmd = [
        'ffmpeg','-hide_banner', '-loglevel', 'error', '-y', '-i', file,
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

    output_mpd = f"{file_id}.mpd"
    # Add DASH options and output MPD file path
    ffmpeg_cmd.extend(dash_options)
    ffmpeg_cmd.append(output_mpd)

    # Run the FFmpeg command for DASH
    subprocess.run(ffmpeg_cmd)

    # Generate thumbnail
    scale_thumbnails = "scale='if(gt(a,16/9),320,-2)':'if(gt(a,16/9),-2,180)',pad=320:180:(ow-iw)/2:(oh-ih)/2:black"
    thumbnail_path = f"thumbnail_{file_id}.jpg"
    thumbnail_cmd = [
        'ffmpeg','-hide_banner', '-loglevel', 'error', '-y', '-i', file,
        '-vf', scale_thumbnails, '-vframes', '1', thumbnail_path
    ]
    subprocess.run(thumbnail_cmd)

    upload_directory(output_path, S3_BUCKET, "videos")
    return

