import datetime

from bson import ObjectId
from flask import url_for, request, redirect
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_restful import Resource, reqparse
from flask_api import status

from config.oauth_client import spotify
from enums.status import Status
from models.event import EventModel
from models.user import UserModel
from models.song import SongModel


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
        user.save_to_db()

        expires = datetime.timedelta(hours=1)
        access_token = create_access_token(identity=str(user.id), fresh=True, expires_delta=expires)

        return redirect(location=f"http://localhost:3000/event?access_token={access_token}&spotify_access_token={spotify_access_token}")


class ExportPlaylist(Resource):
    @classmethod
    @jwt_required
    def post(cls, event_id: str):
        parser = reqparse.RequestParser()
        parser.add_argument('playlist_name', type=str, required=True)
        parser.add_argument('description', type=str, required=True)
        parser.add_argument('public', type=str, default='false', choices=('true', 'false'))
        data = parser.parse_args()

        if not ObjectId.is_valid(event_id):
            return {"status": Status.INVALID_DATA, "message": "Id is not valid ObjectId"}, 400
        event = EventModel.find_by_id(ObjectId(event_id))
        if not event:
            return {"status": Status.NOT_FOUND, "message": "Event not found"}, 403

        current_userid = get_jwt_identity()
        current_user = UserModel.find_by_id(ObjectId(current_userid))
        if not current_user:
            return {"status": Status.USER_NOT_FOUND, "message": "Current user not found"}, 403

        spotify_access_token = request.headers.get('spotify_access_token')
        if not spotify_access_token:
            return {"status": Status.SPOTIFY_TOKEN_MISSING, "message": "header with spotify_access_token is missing"}, 400

        create_playlist_response = cls.create_playlist_in_spotify(current_user.spotify_id, data, spotify_access_token)

        if not status.is_success(create_playlist_response.status):
            return {"status": Status.INVALID_SPOTIFY_TOKEN, "spotify_error": create_playlist_response.data['error']}, 400

        spotify_playlist_id = create_playlist_response.data['id']

        add_tracks_response = cls.add_tracks_to_spotify_playlist(spotify_playlist_id, event.playlist, spotify_access_token)

        if not status.is_success(add_tracks_response.status):
            return {"status": Status.INVALID_SPOTIFY_TOKEN, "spotify_error": create_playlist_response.data['error']}, 400

        return {"status": Status.SUCCESS, "message": "Playlist was imported to your spotify"}, 200

    @classmethod
    def create_playlist_in_spotify(cls, user_spotify_id, data, spotify_access_token):
        request_body = {'name': data['playlist_name'], 'description': data['description'], 'public': data['public']}
        return spotify.post(f'users/{user_spotify_id}/playlists', data=request_body, format='json', token=spotify_access_token)

    @classmethod
    def add_tracks_to_spotify_playlist(cls, spotify_playlist_id, playlist, spotify_access_token):
        track_uris = ''.join(list(map(lambda track_id: 'spotify:track:' + track_id + ',', playlist)))
        url = f'https://api.spotify.com/v1/playlists/{spotify_playlist_id}/tracks?uris={track_uris}'
        return spotify.post(url, format=None, token=spotify_access_token)
