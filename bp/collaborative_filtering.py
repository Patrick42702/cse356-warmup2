import numpy as np

from static.media.a_ffmpeg_helper import video_id
from .util import db
from bson import ObjectId

def cosine_similarity_matrix(M):
    norm = np.linalg.norm(M, axis=1, keepdims=True)
    norm[norm == 0] = 1  # Avoid division by zero for zero vectors (users with no ratings)
    normalized_matrix = M / norm
    return np.dot(normalized_matrix, normalized_matrix.T)

class CollaborativeFiltering:
    def __init__(self):
        users = list(db.users.find({}))
        videos = list(db.videos.find({}))
        self.video_ids = [video['_id'] for video in videos]
        self.user_to_index = {str(doc['_id']): idx for idx, doc in enumerate(users)}
        self.video_to_index = {str(doc['_id']): idx for idx, doc in enumerate(videos)}

        self.num_users = len(users)
        self.num_videos = len(videos)

        self.M = [[0] * self.num_videos for _ in range(self.num_users)]

        for video in videos:
            for like in video['likes']:
                self.M[self.user_to_index[str(like['user'])]][self.video_to_index[str(video['_id'])]] = like['value']

        if self.num_users > 0 and self.num_videos > 0:
            self.predicted_likes = self.predict_missing_values(np.array(self.M, dtype=np.int32))

        self.new_videos = []

    def add_user(self, user_id):
        self.num_users += 1
        self.user_to_index[user_id] = self.num_users
        self.M.append([0] * self.num_videos)

    def add_video(self, video_id):
        self.num_videos += 1
        self.video_ids.append(video_id)
        self.new_videos.append(video_id)
        self.video_to_index[video_id] = self.num_videos
        for row in self.M: row.append(0)

    def add_like(self, user_id, video_id, value):
        self.M[self.user_to_index[user_id]][self.video_to_index[video_id]] = value
        self.predicted_likes = self.predict_missing_values(np.array(self.M, dtype=np.int32))

    def predict_missing_values(self, M):
        similarity_matrix = cosine_similarity_matrix(M)
        predicted_matrix = M.copy()

        for user in range(self.num_users):
            for video in range(self.num_videos):
                if M[user, video] == 0:  # Only predict if the value is missing (0)
                    # Find users who have rated this video (non-zero values)
                    rated_users = M[:, video] != 0
                    similarities = similarity_matrix[user, rated_users]
                    ratings = M[rated_users, video]

                    # If no other users have rated the video, we cannot predict, so leave it as 0
                    if len(ratings) > 0:
                        # Compute weighted average
                        weighted_sum = np.sum(similarities * ratings)
                        sum_of_similarities = np.sum(np.abs(similarities))
                        if sum_of_similarities > 0:
                            predicted_matrix[user, video] = weighted_sum / sum_of_similarities

        return predicted_matrix

    def get_top_recommendations(self, user_id, watched_video_ids, k):
        # figure out which new videos were processed
        self.new_videos = [ vid for vid in
            db.videos.find({'_id': {'$in': [ObjectId(video) for video in self.new_videos]}})
            if vid['status'] == 'processing']

        if len(watched_video_ids) == 0: # we don't know their preferences
            recommendations =  self.video_ids[:k]
        else:
            watched = np.array([self.video_to_index[vid] for vid in watched_video_ids])
            predictions = self.predicted_likes[self.user_to_index[user_id]]
            num_videos = len(predictions)

            all_indices = np.arange(num_videos)
            unwatched_mask = np.ones(num_videos, dtype=bool)
            unwatched_mask[watched] = False
            unwatched_predictions = predictions[unwatched_mask]
            sorted_unwatched_indices = np.argsort(unwatched_predictions)[::-1]
            top_unwatched_indices = all_indices[unwatched_mask][sorted_unwatched_indices]
            recommendations = top_unwatched_indices[:k]

            if len(recommendations) < k:
                watched_mask = ~unwatched_mask
                watched_predictions = predictions[watched_mask]
                sorted_watched_indices = np.argsort(watched_predictions)[::-1]
                top_watched_indices = all_indices[watched_mask][sorted_watched_indices]
                recommendations = np.concatenate([recommendations, top_watched_indices[:k-len(recommendations)]])

        return [self.video_ids[i] for i in recommendations if self.video_ids[i] not in self.new_videos]

rec_algo = CollaborativeFiltering()
