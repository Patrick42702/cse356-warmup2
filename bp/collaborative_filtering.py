import numpy as np

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

    def add_user(self, user_id):
        self.user_to_index[user_id] = self.num_users
        self.num_users += 1
        self.M.append([0] * self.num_videos)
        self.predicted_likes = np.vstack((self.predicted_likes, np.zeros(self.num_videos)))

    def add_video(self, video_id):
        print(f"Added video {video_id}")
        self.video_to_index[video_id] = self.num_videos
        self.num_videos += 1
        self.video_ids.append(ObjectId(video_id))
        print("PREDICTED LIKES, NUM USERS")
        print(self.predicted_likes)
        print(self.predicted_likes.shape)
        print(self.num_users)
        self.predicted_likes = np.hstack((self.predicted_likes, np.zeros((self.num_users,1))))
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
        all_videos = [vid for vid in db.videos.find()]
        sorted_videos = sorted(all_videos, key=lambda vid: len(vid['likes']), reverse=True)
        return [str(vid['_id']) for vid in sorted_videos[:k]]

        processing_videos = [str(vid['_id']) for vid in db.videos.find({'status':'processing'})]

        if len(watched_video_ids) == 0: # we don't know their preferences
            return [vid for vid in self.video_ids if vid not in processing_videos][:k]
        else:
            watched = np.array([self.video_to_index[vid] for vid in watched_video_ids])
            predictions = self.predicted_likes[self.user_to_index[user_id]]

            all_indices = np.arange(self.num_videos)
            print(all_indices)
            unwatched_mask = np.ones(self.num_videos, dtype=bool)
            unwatched_mask[watched] = False
            unwatched_predictions = predictions[unwatched_mask]
            print(unwatched_mask)
            sorted_unwatched_indices = np.argsort(unwatched_predictions)[::-1]
            print(sorted_unwatched_indices)
            top_unwatched_indices = all_indices[unwatched_mask][sorted_unwatched_indices]
            recommendations = top_unwatched_indices
            print("Unwatched recommendations: ", recommendations)

            if len(recommendations) < k:
                watched_mask = ~unwatched_mask
                watched_predictions = predictions[watched_mask]
                sorted_watched_indices = np.argsort(watched_predictions)[::-1]
                top_watched_indices = all_indices[watched_mask][sorted_watched_indices]
                recommendations = np.concatenate([recommendations, top_watched_indices[:k-len(recommendations)]])
                print("All recommendations: ", recommendations)

        return [self.video_ids[i] for i in recommendations if str(self.video_ids[i]) not in processing_videos][:k]

rec_algo = CollaborativeFiltering()
