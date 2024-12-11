from locust import HttpUser, TaskSet, task, constant
from requests_toolbelt.multipart.encoder import MultipartEncoder
import random

class UserBehavior(TaskSet):
    def on_start(self):
        """Executed when a simulated user starts a session."""
        # Login to the app (if needed)
        self.client.post("/api/login", json={"username": "admin", "password": "padmen"})

        # Initialize video ID list
        response = self.client.post("/api/videos", json={"count": 50})
        if response.status_code == 200:
            data = response.json()
            self.video_ids = [video["id"] for video in data.get("videos", [])]
        else:
            quit()

    # @task(1)
    def post_video(self):
        """Test the /api/videos route."""
        if self.video_ids:  # Ensure the list is not empty
            video_id = random.choice(self.video_ids)
            payload = {
                "videoId": video_id,
                "count": 10
            }
            with self.client.post("/api/videos", json=payload, catch_response=True) as response:
                if response.status_code != 200:
                    response.failure(f"Failed to post video: {response.text}")
        else:
            print("No video IDs available to post.")

    # @task(1)
    def post_like(self):
        """Test the /api/like route."""
        if self.video_ids:  # Ensure the list is not empty
            like_id = random.choice(self.video_ids)
            value = random.choice([1, -1])
            payload = {
                "id": like_id,
                "value": value
            }
            with self.client.post("/api/like", json=payload, catch_response=True) as response:
                if response.status_code != 200:
                    response.failure(f"Failed to post like: {response.text}")
        else:
            print("No video IDs available to like.")

    @task(1)
    def upload_mp4(self):
        """Test the /api/upload route with an MP4 file."""
        file_path = "/home/patrick/Downloads/215926_medium.mp4"  # Update this to the actual file path
        with open(file_path, "rb") as mp4_file:
            # Prepare the form data
            multipart_data = MultipartEncoder(
                fields={
                    "author": "John Doe",
                    "title": "Sample Video",
                    "description": "This is a sample video upload.",
                    "mp4File": ("video.mp4", mp4_file, "video/mp4"),
                }
            )
            # Send the POST request
            headers = {"Content-Type": multipart_data.content_type}
            with self.client.post("/api/upload", data=multipart_data, headers=headers, catch_response=True) as response:
                if response.status_code != 200:
                    response.failure(f"Failed to upload MP4: {response.text}")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = constant(0.1)  # Simulate users waiting between requests
    host = "https://esk-pj-air.cse356.compas.cs.stonybrook.edu"
