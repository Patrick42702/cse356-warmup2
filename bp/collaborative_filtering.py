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
        self.con.delete('likes', 'like_count', 'video_ids', 'u2i', 'v2i', 'num_users', 'num_videos')
        users = list(db.users.find({}))
        videos = list(db.videos.find({}))
        video_ids = [str(video['_id']) for video in videos]  # String ID
        u2i = {str(doc['_id']): idx for idx, doc in enumerate(users)}  # String ID
        v2i = {str(doc['_id']): idx for idx, doc in enumerate(videos)}  # String ID
        for video in videos: self.con.hset('like_count', str(video['_id']), '0')
        self.con.rpush('video_ids', *video_ids)
        self.con.hset('u2i', mapping=u2i)
        self.con.hset('v2i', mapping=v2i)
        self.con.set('num_users', len(users))
        self.con.set('num_videos', len(videos))

    def build_matrix(self, likes, u2i, v2i):
        M = np.zeros((len(u2i), len(v2i)), dtype=np.int8)
        for key, value in likes.items():
            user_id, video_id = key.split(',')
            M[int(u2i[user_id])][int(v2i[video_id])] = int(value)
        return M

    def add_user(self, user_id):
        num_users = self.con.incr('num_users')
        self.con.hset('u2i', user_id, num_users-1)

    def add_video(self, video_id):
        self.con.rpush('video_ids', video_id)
        num_videos = self.con.incr('num_videos')
        self.con.hset('v2i', video_id, num_videos-1)

    def add_like(self, user_id, video_id, value):
        key = f'{user_id},{video_id}'
        prev_value = self.con.hget('likes', key)
        if prev_value == value: return -1
        self.con.hset('likes', key, value)
        return self.con.hincrby('like_count', video_id, 1 if value=='1' else (-1 if prev_value == '1' else 0))

    def user_based_recommendations(self, user_id, watched, count, ready_to_watch=False):
        likes, u2i, v2i, video_ids = self.con.pipeline().hgetall('likes').hgetall('u2i').hgetall('v2i').lrange('video_ids', 0, -1).execute()
        M = self.build_matrix(likes, u2i, v2i)
        user_idx = int(u2i[user_id])
        watched = [int(v2i[vid]) for vid in watched]

        similarities = np.dot(M, M[user_idx])  # might need to change to cosine similarity
        predictions = np.dot(similarities, M)  # how our user would rate each video
        recommendations = np.argsort(predictions)[::-1]  # sort indices from highest to lowest rating
        watched_mask = np.isin(recommendations, watched)
        recommendations = np.concatenate((recommendations[~watched_mask], recommendations[watched_mask]))  # prioritize unwatched videos
        logger.info(f"Total of {len(recommendations)} videos retrieved")
        processing_videos = {str(vid['_id']) for vid in db.videos.find({'status': 'processing'})} if ready_to_watch else set()
        final_video_list = list(islice((ObjectId(vid_id) for vid_idx in recommendations if (vid_id := video_ids[vid_idx]) not in processing_videos), count))
        logger.info(f"Total of {len(final_video_list)} videos returned")
        return final_video_list

    def video_based_recommendations(self, video_id, watched, count, ready_to_watch=False):
        likes, u2i, v2i, video_ids = self.con.pipeline().hgetall('likes').hgetall('u2i').hgetall('v2i').lrange('video_ids', 0, -1).execute()
        M = self.build_matrix(likes, u2i, v2i)
        video_idx = int(u2i[video_id])
        watched = [int(v2i[vid]) for vid in watched]

        similarities = np.dot(M[:, video_idx], M)  # how similar is each video to our video
        recommendations = np.argsort(similarities)[::-1]  # sort indices from highest to lowest rating
        watched_mask = np.isin(recommendations, watched)
        recommendations = np.concatenate((recommendations[~watched_mask], recommendations[watched_mask]))  # prioritize unwatched videos
        logger.info(f"Total of {len(recommendations)} videos retrieved")
        processing_videos = {str(vid['_id']) for vid in db.videos.find({'status': 'processing'})} if ready_to_watch else set()
        final_video_list = list(islice((ObjectId(vid_id) for vid_idx in recommendations if (vid_id := video_ids[vid_idx]) not in processing_videos), count))
        logger.info(f"Total of {len(final_video_list)} videos returned")
        return final_video_list

rec_algo = CollaborativeFiltering()
