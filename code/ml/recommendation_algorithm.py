import spotipy
import sys
import spotipy.util as util
from surprise import SVD
import pprint
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import oauth2

username = 'filip'
scope = 'user-library-read user-top-read'
client_id ='b4e8d875ebc74954a74b53ca13f1761b'
client_secret ='6e7b7779c1bc461a936d3e7bea55eea5'
redirect_uri ='http://localhost:8080'
token = util.prompt_for_user_token(username,
                           scope,
                           client_id,
                           client_secret,
                           redirect_uri)

sp = spotipy.Spotify(auth=token)

class Recommendation_Algorithm_SVD:
    def __init__(self,token,event_id):
        self.event = event_id
        self.token = token
        self.users = []

        for participant in self.event_id.participants:
            self.users.append(UserModel.find_by_id(participant.user_id))
        for user in self.users:
                for song in user.song_ids:
                    artists_id = sp.track(song)['artist_id']
                    for artist_id in artists_id:
                        sp.artist(artist)