import os
import subprocess
import time
import requests


def download_and_extract_videos():
    # Download videos
    # Define the directory and video URL
    cwd = os.getcwd()
    video_dir = f"{cwd}/static/tmp"
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)
    os.chdir(video_dir)
    subprocess.run(["wget", "-r", "-l1", "-A", "*.mp4", "-A", "*.json", "-nd", "-P", "videos", "http://130.245.136.73/mnt2/video/m2.html"])

def run_docker_compose():
    # Run docker-compose up
    print("Starting Docker Compose...")
    subprocess.run(["docker", "compose", "up", "-d"], check=True)
    print("Docker Compose services started.")

if __name__ == "__main__":
    download_and_extract_videos()
    run_docker_compose()
    time.sleep(10)
    cwd = os.getcwd()
    video_dir = f"{cwd}/static/tmp/videos"
    for file in os.listdir(video_dir):
        if file.endswith(".mp4"):
            data = {
                'title': 'Your Video Title',
                'author': 'Author Name'
            }
            # Define the file to upload
            files = {
                'mp4file': (f'{file}.mp4', open(f'{video_dir}/{file}', 'rb'), 'video/mp4')
            }

            requests.post("http://localhost:5050/api/upload", data=data, files=files)
