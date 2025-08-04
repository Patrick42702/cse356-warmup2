import json
import os
import subprocess

import boto3
import requests

TEMP_VIDEO_DIRECTORY = os.environ.get("TEMP_VIDEO_DIRECTORY")
S3_BUCKET = os.environ.get("S3_BUCKET")
PROCESSING = os.environ.get("PROCESSING")
PROCESSED = os.environ.get("PROCESSED")

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
            if not file.startswith("init_") and ".mp4" in file:
                continue
            full_path = os.path.join(root, file)
            s3_key = f"{prefix}/{file}"
            print(f"Uploading file: {file}")
            try:
                s3.upload_file(full_path, bucket, s3_key)
            except Exception as e:
                print(f"Upload failed for {file}: {e}")

def transcode_to_mpeg_dash(s3_url, file, file_id, db):
    # Video filter for padding to 16:9 aspect ratio
    output_path = f"{TEMP_VIDEO_DIRECTORY}/{file_id}"
    output_file = os.path.join(output_path, file)

    try:
        # make dir for output path
        os.mkdir(output_path)
        os.chdir(output_path)

        # download mp4 file
        req = requests.get(s3_url, stream=True)
        req.raise_for_status()
        with open(output_file, 'wb') as f:
            for chunk in req.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded to: {output_path}")

        db.videos.update_one({
            "video_id": file_id
        },{"$set": {"status": PROCESSING}})


        # set ffmpeg options
        scale_filter = "scale='if(gt(a,16/9),1280,-2)':'if(gt(a,16/9),-2,720)',pad=1280:720:(ow-iw)/2:(oh-ih)/2:black"
        video_options = [
            ('512k', '640x360'),
            ('768k', '960x540'),
            ('1024k', '1280x720'),
            ('2048k', '1920x1080')
        ]

        audio_options = [
            '64k',
        ]

        dash_options = [
            '-use_template', '1',
            '-use_timeline', '1',
            '-seg_duration', '10',
            '-adaptation_sets', 'id=0,streams=v id=1,streams=a',
            '-f', 'dash', '-copyts', '-start_at_zero', '-avoid_negative_ts', 'make_zero',
        ]
        output_mpd = f"{file_id}.mpd"

        # Start constructing the FFmpeg command
        ffmpeg_cmd = [
            'ffmpeg','-hide_banner', '-loglevel', 'error', '-y',
            "-fflags", "+genpts", '-i', file,
            '-vf', scale_filter, '-report'
        ]

        # Add video bitrates and resolutions
        for i, (bitrate, resolution) in enumerate(video_options):
            ffmpeg_cmd.extend([
                '-map', '0:v:0',
                f'-c:v:{i}', 'libx264',
                f'-b:v:{i}', bitrate,
                f'-s:v:{i}', resolution,
                '-pix_fmt', 'yuv420p',
                f'-profile:v:{i}', 'main',
            ])

        # Add audio streams
        for i, bitrate in enumerate(audio_options):
            ffmpeg_cmd.extend([
                '-map', '0:a:0',
                f'-c:a:{i}', 'aac',
                f'-b:a:{i}', bitrate,
                f'-ac:a:{i}', '2',  # Stereo
                f'-ar:a:{i}', '48000'  # Sample rate
            ])

        ffmpeg_cmd.extend([
            '-init_seg_name', f"init_{file_id}_$RepresentationID$.mp4",
            '-media_seg_name', f"chunk_{file_id}_$Bandwidth$_$Number$.m4s"
        ])

        # Add DASH options and output MPD file path
        ffmpeg_cmd.extend(dash_options)
        ffmpeg_cmd.append(output_mpd)
        print(f"FFmpeg command: {' '.join(ffmpeg_cmd)}")

        # Run the FFmpeg command for DASH
        subprocess.run(ffmpeg_cmd, check=True)

        # Generate thumbnail
        scale_thumbnails = "scale='if(gt(a,16/9),320,-2)':'if(gt(a,16/9),-2,180)',pad=320:180:(ow-iw)/2:(oh-ih)/2:black"
        thumbnail_path = f"thumbnail_{file_id}.jpg"
        thumbnail_cmd = [
            'ffmpeg','-hide_banner', '-loglevel', 'error', '-y', '-i', file,
            '-vf', scale_thumbnails, '-vframes', '1', thumbnail_path
        ]
        subprocess.run(thumbnail_cmd, check=True)

        upload_directory(output_path, S3_BUCKET, f"videos/{file_id}")

        db.videos.update_one({
            "video_id": file_id
        },{"$set": {"status": PROCESSED}})
    except requests.exceptions.RequestException as e:
        print(f"[Error] Download failed: {e}")
    except subprocess.CalledProcessError as e:
        print(f"[Error] FFmpeg failed: {e}")
    except Exception as e:
        print(f"[Error] Unexpected failure: {e}")

    return

