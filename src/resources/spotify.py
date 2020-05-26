import datetime

from flask import url_for, request, redirect
from flask_jwt_extended import create_access_token
from flask_restful import Resource

from config.oauth_client import spotify
from models.song import SongModel
from models.user import UserModel


class SpotifyLogin(Resource):
    @classmethod
    def get(cls):
        return spotify.authorize(url_for("spotify.authorize", _external=True))


class SpotifyAuthorize(Resource):
    @classmethod
    def get(cls):
        response = spotify.authorized_response()

        if response is None or response.get("access_token") is None:
            error_response = {
                "error": request.args["error"],
                "error_description": request.args["error_description"]
            }
            return error_response

        spotify_access_token = response['access_token']

        spotify_user = spotify.get('me', token=spotify_access_token)
        spotify_username = spotify_user.data['display_name']
        spotify_email = spotify_user.data['email']
        spotify_id = spotify_user.data['id']
        spotify_images = spotify_user.data['images']
        avatar_url = spotify_images[0]['url'] if len(spotify_images) > 0 else None

        # add missing tracks

        data = {'limit': 50}
        spotify_user_fav_tracks = spotify.get('me/top/tracks', data=data, token=spotify_access_token).data

        song_ids = []

        for track in spotify_user_fav_tracks['items']:
            song_ids.append(track['id'])
            if SongModel.find_by_id(track['id']) is None:
                track_artists = [x['name'] for x in track['artists']]
                track_artists_ids = [x['id'] for x in track['artists']]
                image_url = track['album']['images'][0]['url'] if len(track['album']['images']) > 0 else None
                genres = list(set([item for sublist in
                                   [spotify.get('artists/' + x, token=spotify_access_token).data['genres'] for x in
                                    track_artists_ids] for item in sublist]))

                song = SongModel(track_id=track['id'], name=track['name'], album=track['album']['name'],
                                 artist=track_artists, genres=genres, duration=track['duration_ms'], image_url=image_url)

                song.save_to_db()

        user = UserModel.find_by_email(spotify_email)

        if not user:
            user = UserModel(username=spotify_username, email=spotify_email, password=None, spotify_id=spotify_id, avatar_url=avatar_url, song_ids=song_ids)
        else:
            user.song_ids = song_ids
            user.spotify_id = spotify_id
            user.avatar_url = avatar_url
        user.save_to_db()

        expires = datetime.timedelta(hours=1)
        access_token = create_access_token(identity=str(user.id), fresh=True, expires_delta=expires)

        return redirect(location=f"https://joyina.live/event?access_token={access_token}&spotify_access_token={spotify_access_token}")
