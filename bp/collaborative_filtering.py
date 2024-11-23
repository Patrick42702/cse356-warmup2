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
        self.redis_client = redis.Redis(host='redis')
        self.lock = self.redis_client.lock('M', timeout=10)
        users = list(db.users.find({}))
        videos = list(db.videos.find({}))
        video_ids = [str(video['_id']) for video in videos]  # String ID
        u2i = {str(doc['_id']): idx for idx, doc in enumerate(users)}  # String ID
        v2i = {str(doc['_id']): idx for idx, doc in enumerate(videos)}  # String ID
        M = np.zeros((len(users), len(videos)), dtype=np.int8)
        for video in videos:
            for like in video['likes']:
                M[u2i[str(like['user'])], v2i[str(video['_id'])]] = like['value']

        self.save_to_redis(M)
        self.redis_client.rpush('video_ids', *video_ids)
        self.redis_client.hset('u2i', mapping=u2i)
        self.redis_client.hset('v2i', mapping=v2i)

    def save_to_redis(self, M):
        buffer = io.BytesIO()
        np.save(buffer, M)
        buffer.seek(0)
        self.redis_client.set('M', buffer.read())

    def read_from_redis(self, get_video_ids=False):
        data = self.redis_client.get('M')
        buffer = io.BytesIO(data)
        M = np.load(buffer)
        if get_video_ids:
            video_ids = [vid.decode() for vid in self.redis_client.lrange('video_ids', 0, -1)]
            return M, video_ids
        return M

    def add_user(self, user_id):
        with self.lock:
            M = self.read_from_redis()
            self.redis_client.hset('u2i', user_id, M.shape[0])
            M = np.vstack((M, np.zeros(M.shape[1], np.int8)))
            self.save_to_redis(M)

    def add_video(self, video_id):
        with self.lock:
            M = self.read_from_redis()
            self.redis_client.rpush('video_ids', video_id)
            self.redis_client.hset('v2i', video_id, M.shape[1])
            M = np.hstack((M, np.zeros((M.shape[0], 1), np.int8)))
            self.save_to_redis(M)

    def add_like(self, user_id, video_id, value):
        with self.lock:
            M = self.read_from_redis()
            user_idx = self.redis_client.hget('u2i', user_id)
            video_idx = self.redis_client.hget('v2i', video_id)
            M[user_idx, video_idx] = value
            self.save_to_redis(M)

    def user_based_recommendations(self, user_id, watched, count, ready_to_watch=False):
        user_idx = int(self.redis_client.hget('u2i', user_id))
        v2i = self.redis_client.hgetall('v2i')
        M, video_ids = self.read_from_redis(get_video_ids=True)
        # logger.debug(f'[Colab Filter] User {user_id} has liked the following videos: {[self.video_ids[i] for i, val in enumerate(M[user_idx]) if val==1]}')
        similarities = np.dot(M, M[user_idx])  # might need to change to cosine similarity
        predictions = np.dot(similarities, M)  # how our user would rate each video
        recommendations = np.argsort(predictions)[::-1]  # sort indices from highest to lowest rating
        watched = [int(v2i[vid.encode()]) for vid in watched]
        watched_mask = np.isin(recommendations, watched)
        recommendations = np.concatenate((recommendations[~watched_mask], recommendations[watched_mask]))  # prioritize unwatched videos
        processing_videos = {str(vid['_id']) for vid in db.videos.find({'status': 'processing'})} if ready_to_watch else set()
        return list(islice((ObjectId(vid_id) for vid_idx in recommendations if (vid_id := video_ids[vid_idx]) not in processing_videos), count))

    def video_based_recommendations(self, video_id, watched, count, ready_to_watch=False):
        v2i = self.redis_client.hgetall('v2i')
        M, video_ids = self.read_from_redis(get_video_ids=True)
        video_idx = int(v2i[video_id.encode()])
        # logger.debug(f'[Colab Filter] Video {video_id} liked column: {M[:, video_idx]}')
        similarities = np.dot(M[:, video_idx], M)  # how similar is each video to our video
        recommendations = np.argsort(similarities)[::-1]  # sort indices from highest to lowest rating
        watched = [v2i[vid] for vid in watched]
        watched_mask = np.isin(recommendations, watched)
        recommendations = np.concatenate((recommendations[~watched_mask], recommendations[watched_mask]))  # prioritize unwatched videos
        processing_videos = {str(vid['_id']) for vid in db.videos.find({'status': 'processing'})} if ready_to_watch else set()
        final_video_list = list(islice((ObjectId(vid_id) for vid_idx in recommendations if (vid_id := video_ids[vid_idx]) not in processing_videos), count))
        # logger.debug(f"{M}\nSimilarities: {similarities}\nRecommendations: {recommendations}\nFinal: {final_video_list}")
        return final_video_list

rec_algo = CollaborativeFiltering()