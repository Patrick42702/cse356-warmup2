import os
import subprocess
import time
import requests
import json

def download_m2json():
    cwd = os.getcwd()
    video_dir = f"{cwd}/static/tmp"
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)
    else:
        return
    os.chdir(video_dir)
    if os.path.exists(f"{video_dir}/videos/m2.json"):
        return
    else:
        subprocess.run(["wget", "-r", "-l1", "-A", "*.json", "-nd", "-P", "videos", "http://130.245.136.73/mnt2/video/m2.html"])


def download_and_extract_videos():
    # Download videos
    # Define the directory and video URL
    cwd = os.getcwd()
    video_dir = f"{cwd}/videos"
    os.chdir(video_dir)
    with open("m2.json", "r") as f:
        data = dict(json.load(f))

    # only download video if it doesn't exist
    for video in data:
        if not os.path.exists(f"{video_dir}/{video}"):
            subprocess.run(["wget", "-r", "-l1", "-A", f"{video}", "http://130.245.136.73/mnt2/video/m2.html"])
    return

def run_docker_compose():
    # Run docker-compose up
    print("Starting Docker Compose...")
    subprocess.run(["docker", "compose", "up", "-d"], check=True)
    print("Docker Compose services started.")
    return

if __name__ == "__main__":
    download_m2json()
    download_and_extract_videos()
    run_docker_compose()
    time.sleep(10)
    cwd = os.getcwd()
    video_dir = f"{cwd}/static/tmp/videos"
    meta = f"{video_dir}/m2.json"
    os.chdir(video_dir)
    with open(f"{meta}", "r") as f:
        data = dict(json.load(f))
    for video in data:
        form = {
            'title': video['title'],
            'author': "CSE356 Team"
        }

        files = {
            'mp4file': (open(f'{video_dir}/{video}', 'rb'), 'video/mp4')
        }

        requests.post("http://localhost:5050/api/upload", data=form, files=files)


