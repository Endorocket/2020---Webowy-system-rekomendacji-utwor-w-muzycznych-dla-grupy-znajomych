import numpy as np
import pandas as pd
import traceback
from surprise import SVD,Dataset,Reader
from bson import ObjectId
from models.song import SongModel
from models.user import UserModel
from models.event import EventModel
from collections import Counter
from random import shuffle

class RecommendationAlgorithmSVD:
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
                song_genres = SongModel.find_by_id(song_id).genres
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
            try:
                results[event.participants.index(uid)][genre_list.index(iid)] = est
            except ValueError:
                traceback.print_exc()
                
        results = scores_matrix + results
        cumulative_scores = np.apply_along_axis(sum, 0, results)
        if np.sum(cumulative_scores) != 0:
            probabilities = cumulative_scores / np.sum(cumulative_scores)
        else:
            probabilities = (cumulative_scores + 1)/np.ma.count(genre_list)

        #playlist_duration = 0
        playlist = []
        event_duration_in_ms = event.duration_time*60*60*1000
        avg_song_time = 180000
        songs_in_playlist = int(event_duration_in_ms/avg_song_time) if event_duration_in_ms > 0 else 50


        chosen_genres = np.random.choice(genre_list, songs_in_playlist, p=probabilities)
        genre_count = Counter(chosen_genres)
        songs = SongModel.random_from_genres(genre_count)
        shuffle(songs)
        for song in songs:
            if song['_id'] not in playlist:
                song['track_id'] = song.pop('_id')
                playlist.append(song)
                #playlist_duration += song['duration']
        return playlist