import spotipy
import sys
import spotipy.util as util
import numpy as np
import pandas as pd
from surprise import SVD
from surprise import Dataset
from surprise import Reader
from collections import defaultdict
import pprint
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import oauth2

'''username = 'f'
scope = 'user-library-read user-top-read'
client_id ='b4e8d875ebc74954a74b53ca13f1761b'
client_secret ='6e7b7779c1bc461a936d3e7bea55eea5'
redirect_uri ='http://localhost:8080'
token = util.prompt_for_user_token(username,
                           scope,
                           client_id,
                           client_secret,
                           redirect_uri)'''

sp = spotipy.Spotify(auth=token)


class Recommendation_Algorithm_SVD:
    def __init__(self,token,event_id,db):
        self.event = event_id
        self.token = token
        self.db = db
        self.users = []
        self.genre_list = db.songs.find().distinct('genres')
        self.scores_matrix = np.zeros((len(event_id.participants),len(self.genre_list)))


        for participant in self.event_id.participants:
            self.users.append(UserModel.find_by_id(participant.user_id))
        for user in self.users:
                for song in user.song_ids:
                    artists_id = sp.track(song)['artist_id']
                    for artist_id in artists_id['items']:
                        genres = sp.artist(artist_id)['genres']
                        for genre in genres:
                            self.genre_list[self.genre_list.index(genre)] += 1

        ratings_dict = {'itemID': [],
                        'userID': [],
                        'rating': []}

        for i in range(self.scores_matrix.shape[0]):
            for j in range(self.scores_matrix.shape[1]):
                if self.scores_matrix[i][j] != 0:
                    ratings_dict['itemID'].append(self.genre_list[i])
                    ratings_dict['userID'].append(self.event['users'][j])
                    ratings_dict['rating'].append(self.scores_matrix[i][j])

        df = pd.DataFrame(ratings_dict)

        reader = Reader()

        data = Dataset.load_from_df(df[['userID', 'itemID', 'rating']], reader)

        trainset = data.build_full_trainset()


        algorithm = SVD()
        algorithm.fit(trainset)

        testset = trainset.build_anti_testset()
        predictions = algorithm.test(testset)

        top_n_predictions = self.get_top_n_for_user(predictions,10)


        def get_top_n_for_user(self, predictions, n=10):

            top_n = defaultdict(list)
            for uid, iid, est in predictions:
                top_n[uid].append((iid, est))

            for uid, user_ratings in top_n.items():
                user_ratings.sort(key=lambda x: x[1], reverse=True)
                top_n[uid] = user_ratings[:n]

            return top_n
