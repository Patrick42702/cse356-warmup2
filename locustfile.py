from locust import HttpUser, TaskSet, task, constant
import random
import httpx

class UserBehavior(TaskSet):
    def on_start(self):
        """Executed when a simulated user starts a session."""
        # Login to the app (if needed)
        self.client = httpx.Client(http2=True, base_url=self.parent.host)
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
            response = self.client.post("/api/videos", json=payload, catch_response=True)
            if response.status_code != 200:
                response.failure(f"Failed to post video: {response.text}")
        else:
            print("No video IDs available to post.")

    @task(1)
    def post_like(self):
        """Test the /api/like route."""
        if self.video_ids:  # Ensure the list is not empty
            like_id = random.choice(self.video_ids)
            value = random.choice([1, -1])
            payload = {
                "id": like_id,
                "value": value
            }
            response = self.client.post("/api/like", json=payload, catch_response=True)
            if response.status_code != 200:
                response.failure(f"Failed to post like: {response.text}")
        else:
            print("No video IDs available to like.")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = constant(0.1)  # Simulate users waiting between requests
    host = "https://esk-pj-air.cse356.compas.cs.stonybrook.edu"
