import numpy as np
import pandas as pd
from surprise import SVD,Dataset,Reader
from collections import defaultdict,Counter
from bson import ObjectId
from models.song import SongModel
from models.user import UserModel
from models.event import EventModel


class Recommendation_Algorithm_SVD:
    @classmethod
    def run(cls,event_id):

        event = EventModel.find_by_id(ObjectId(event_id))
        genre_list = SongModel.find_all_genres()

        spotify_users = []
        non_spotify_users = []
        scores_matrix = np.zeros((len(event.participants),len(genre_list)))

        for participant in event.participants:
            user = UserModel.find_by_id(ObjectId(participant.user_id))
            if user.song_ids:
                spotify_users.append(user)
            else:
                non_spotify_users.append(user)

        for spotify_user in spotify_users:
            for song_id in spotify_user.song_ids:
                song_genres = SongModel.find_by_id(ObjectId(song_id)).genres
                for song_genre in song_genres:
                    scores_matrix[spotify_users.index(spotify_user)][genre_list.index(song_genre)] += 1

        max_score = np.amax(scores_matrix) if np.amax(scores_matrix)> 0 else 1

        for non_spotify_user in non_spotify_users:
            for pref_genre in non_spotify_user.pref_genres:
                scores_matrix[spotify_users.index(len(spotify_users) + non_spotify_user)][genre_list.index(pref_genre)] = max_score

        ratings_dict = {'itemID': [],
                        'userID': [],
                        'rating': []}

        for i in range(scores_matrix.shape[0]):
            for j in range(scores_matrix.shape[1]):
                if scores_matrix[i][j] != 0:
                    ratings_dict['itemID'].append(genre_list[j])
                    ratings_dict['userID'].append(event.participants[i].user_id)
                    ratings_dict['rating'].append(scores_matrix[i][j])


        df = pd.DataFrame(ratings_dict)
        reader = Reader(rating_scale=(0, max_score))
        data = Dataset.load_from_df(df[['userID', 'itemID', 'rating']], reader)
        trainset = data.build_full_trainset()

        algorithm = SVD()
        algorithm.fit(trainset)

        testset = trainset.build_anti_testset()
        predictions = algorithm.test(testset)

        results = np.zeros(scores_matrix.shape)
        for uid, iid, _, est, _ in predictions:
            results[event.participants.index(uid)][genre_list.index(iid)] = est
        results = scores_matrix + results
        cumulative_scores = np.apply_along_axis(sum, 0, results)
        if np.sum(cumulative_scores) != 0:
            probabilities = cumulative_scores / np.sum(cumulative_scores)
        else:
            probabilities = (cumulative_scores + 1)/np.ma.count(genre_list)

        playlist_duration = 0
        playlist = []
        event_duration_in_ms = event.duration_time*60*60*1000

        if event_duration_in_ms > 0 :
            while event_duration_in_ms > playlist_duration:
                chosen_genre = np.random.choice(genre_list, 1, p=probabilities)[0]
                song = SongModel.random_from_genre(chosen_genre)
                if song.track_id not in playlist:
                    playlist.append(song.track_id)
                    playlist_duration += song.duration

        else:
            while len(playlist) < 50:
                chosen_genre = np.random.choice(genre_list, 1, p=probabilities)
                song = SongModel.random_from_genre(chosen_genre)
                if song.track_id not in playlist:
                    playlist.append(song.track_id)
                    playlist_duration += song.duration
        print(playlist)
        return playlist







