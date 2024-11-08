import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pymongo import MongoClient
import subprocess

# Base URL
base_url = "http://130.245.136.73/mnt2/video/m2.html"
video_url_prefix = "http://130.245.136.73/mnt2/video/"

# Folder to save videos
media_folder = "static/media"
os.makedirs(media_folder, exist_ok=True)


# Function to get the list of mp4 URLs
def get_mp4_urls(url):
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all links ending with .mp4
    mp4_urls = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and href.endswith(".mp4"):
            full_url = urljoin(video_url_prefix, href)
            mp4_urls.append(full_url)

    return mp4_urls[:30]  # Limit to the first 30 mp4 files


# Function to download a single video
def add_video(url, dest_folder, user_id):
    video_name = os.path.basename(url)
    video_id = db.videos.insert_one({"user": user_id, "author": "admin", "title": video_name, "status": "complete", "likes": []}).inserted_id
    dest_path = f"{dest_folder}/{video_id}/{video_id}.mp4"

    print(f"Downloading {video_name}...")
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        os.makedirs(f"{dest_folder}/{video_id}", exist_ok=True)
        with open(dest_path, 'wb') as file: file.write(response.content)
    print(f"Saved to {dest_path}")
    process_video(dest_path)
    return video_id

def process_video(filepath):
    # Video filter for padding to 16:9 aspect ratio
    scale_filter = "scale='if(gt(a,16/9),1280,-2)':'if(gt(a,16/9),-2,720)',pad=1280:720:(ow-iw)/2:(oh-ih)/2:black"

    # FFmpeg resolution and bitrate options
    ffmpeg_options = [
        ('254k', '320x180'),
        ('507k', '320x180'),
        ('759k', '480x270'),
        ('1013k', '640x360'),
        ('1254k', '640x360'),
        ('1883k', '768x432'),
        ('3134k', '1024x576'),
        ('4952k', '1280x720')
    ]

    # DASH options
    dash_options = [
        '-use_template', '1',
        '-use_timeline', '1',
        '-seg_duration', '10',
        '-adaptation_sets', 'id=0,streams=v',
        '-f', 'dash'
    ]

    owd = os.getcwd()
    cwd = os.path.dirname(filepath)
    os.chdir(cwd)

    filename = filepath.split('/')[-1]
    file_id = filename.split('.')[0]
    output_mpd = f"{file_id}.mpd"
    input_path = f'{cwd}/{filename}'
    print(f"{filename} is the filename, {input_path} is the input path, and {file_id} is the file id")


    # Start constructing the FFmpeg command
    ffmpeg_cmd = [
        'ffmpeg', '-y', '-i', filename,
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
    print(f"Processing {filename} with video ID {file_id}")
    subprocess.run(ffmpeg_cmd)

    # Generate thumbnail
    scale_thumbnails = "scale='if(gt(a,16/9),320,-2)':'if(gt(a,16/9),-2,180)',pad=320:180:(ow-iw)/2:(oh-ih)/2:black"
    thumbnail_path = f"thumbnail_{file_id}.jpg"
    thumbnail_cmd = [
        'ffmpeg', '-y', '-i', filename,
        '-vf', scale_thumbnails, '-vframes', '1', thumbnail_path
    ]
    print(f"Generating thumbnail for {filename} with video ID {file_id}")
    subprocess.run(thumbnail_cmd)
    os.chdir(owd)
    print("Processing complete.")
    return filepath


# Main execution
if __name__ == "__main__":
    db = MongoClient('localhost', 27017).eskpj_airplanes
    admin_id = db.users.insert_one({"username": "admin", "password": "padmen",
                      "email": "admin@admin.pop", "validated": True,
                      "videos": [], "watched": [], "verify-key": "whatever"}).inserted_id

    mp4_urls = get_mp4_urls(base_url)
    print(f"Found {len(mp4_urls)} video files to download.")

    video_ids = []
    for url in mp4_urls:
        video_ids.append(add_video(url, media_folder, admin_id))
    db.users.update({"_id": admin_id}, {"$set": {"videos": video_ids}})

    print("Downloaded 30 videos to the tmp folder.")