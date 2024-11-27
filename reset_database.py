import os
import shutil
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017/")
db = client["eskpj_airplanes"]
users = db["users"]
videos = db["videos"]

all_video_ids = [str(vid['_id']) for vid in videos.find({}, {"_id": 1}).sort("_id", 1)]
original_video_ids = set(all_video_ids[:50])

non_original_video_ids = [x for x in os.listdir("static/media") if x not in original_video_ids]


print(f"Deleting {len(non_original_video_ids)} video folders.")
base_path = "static/media"
for video_id in non_original_video_ids:
    dir_path = os.path.join(base_path, video_id)
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        shutil.rmtree(dir_path)
    else:
        print(f"Directory not found: {dir_path}")

print("Removing non-admin users: " + str(users.delete_many({ 'username': { '$ne': 'admin' } })))
print("Removing watches from admin" + str(users.update_many({}, {'$set':{'watched':[]}})))
print("Removing non-existent videos: " + str(videos.delete_many({"_id": {"$in": [ObjectId(vid) for vid in non_original_video_ids]}})))
print("Removing remaining likes: " + str(videos.update_many({}, {'$set':{'likes':[]}})))
