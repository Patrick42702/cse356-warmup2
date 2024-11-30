import sys
import io
import numpy as np
from itertools import islice
from .log_util import get_logger
from .util import db
import redis
from bson import ObjectId

logger = get_logger("/api/videos")

class CollaborativeFiltering:
    def __init__(self):
        self.con = redis.Redis(host='redis', decode_responses=True)
        self.con.delete('likes', 'video_ids', 'u2i', 'v2i', 'num_users', 'num_videos')
        users = list(db.users.find({}))
        videos = list(db.videos.find({}))
        video_ids = [str(video['_id']) for video in videos]  # String ID
        u2i = {str(doc['_id']): idx for idx, doc in enumerate(users)}  # String ID
        v2i = {str(doc['_id']): idx for idx, doc in enumerate(videos)}  # String ID
        for video in videos:
            for like in video['likes']:
                self.set_like(u2i[str(like['user'])], v2i[str(video['_id'])], like['value'])
        self.con.rpush('video_ids', *video_ids)
        self.con.hset('u2i', mapping=u2i)
        self.con.hset('v2i', mapping=v2i)
        self.con.set('num_users', len(users))
        self.con.set('num_videos', len(videos))

    def set_like(self, user_idx, video_idx, value):
        self.con.hset('likes', str(user_idx) + "," + str(video_idx), value)

    def build_matrix(self):
        num_users = int(self.con.get('num_users'))
        num_videos = int(self.con.get('num_videos'))
        likes = self.con.hgetall('likes')
        M = np.zeros((num_users, num_videos), dtype=np.int8)
        for key, value in likes.items():
            user_idx, video_idx = key.split(',')
            M[int(user_idx)][int(video_idx)] = int(value)
        return M

    def add_user(self, user_id):
        num_users = self.con.incr('num_users')
        self.con.hset('u2i', user_id, num_users-1)

    def add_video(self, video_id):
        self.con.rpush('video_ids', video_id)
        num_videos = self.con.incr('num_videos')
        self.con.hset('v2i', video_id, num_videos-1)

    def add_like(self, user_id, video_id, value):
        user_idx = int(self.con.hget('u2i', user_id))
        video_idx = int(self.con.hget('v2i', video_id))
        self.set_like(user_idx, video_idx, value)

    def user_based_recommendations(self, user_id, watched, count, ready_to_watch=False):
        user_idx = int(self.con.hget('u2i', user_id))
        v2i = self.con.hgetall('v2i')
        video_ids = self.con.lrange('video_ids', 0, -1)
        M = self.build_matrix()
        similarities = np.dot(M, M[user_idx])  # might need to change to cosine similarity
        predictions = np.dot(similarities, M)  # how our user would rate each video
        recommendations = np.argsort(predictions)[::-1]  # sort indices from highest to lowest rating
        watched = [int(v2i[vid]) for vid in watched]
        watched_mask = np.isin(recommendations, watched)
        recommendations = np.concatenate((recommendations[~watched_mask], recommendations[watched_mask]))  # prioritize unwatched videos
        processing_videos = {str(vid['_id']) for vid in db.videos.find({'status': 'processing'})} if ready_to_watch else set()
        return list(islice((ObjectId(vid_id) for vid_idx in recommendations if (vid_id := video_ids[vid_idx]) not in processing_videos), count))

    def video_based_recommendations(self, video_id, watched, count, ready_to_watch=False):
        v2i = self.con.hgetall('v2i')
        video_ids = self.con.lrange('video_ids', 0, -1)
        M = self.build_matrix()
        video_idx = int(v2i[video_id])
        similarities = np.dot(M[:, video_idx], M)  # how similar is each video to our video
        recommendations = np.argsort(similarities)[::-1]  # sort indices from highest to lowest rating
        watched = [int(v2i[vid]) for vid in watched]
        watched_mask = np.isin(recommendations, watched)
        recommendations = np.concatenate((recommendations[~watched_mask], recommendations[watched_mask]))  # prioritize unwatched videos
        processing_videos = {str(vid['_id']) for vid in db.videos.find({'status': 'processing'})} if ready_to_watch else set()
        final_video_list = list(islice((ObjectId(vid_id) for vid_idx in recommendations if (vid_id := video_ids[vid_idx]) not in processing_videos), count))
        return final_video_list

rec_algo = CollaborativeFiltering()
