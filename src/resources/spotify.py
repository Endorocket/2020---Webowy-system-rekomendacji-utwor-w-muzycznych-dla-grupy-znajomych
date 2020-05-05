import datetime

from bson import ObjectId
from flask import url_for, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_restful import Resource, reqparse

from config.oauth_client import spotify
from models.event import EventModel
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

        user = UserModel.find_by_email(spotify_email)

        if not user:
            user = UserModel(username=spotify_username, email=spotify_email, password=None, spotify_id=spotify_id, avatar_url=avatar_url)
            user.save_to_db()

        expires = datetime.timedelta(hours=1)
        access_token = create_access_token(identity=str(user.id), fresh=True, expires_delta=expires)

        return {"access_token": access_token}


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
            return {"message": "Id is not valid ObjectId"}, 400
        event = EventModel.find_by_id(ObjectId(event_id))
        if not event:
            return {"message": "Event not found"}, 403

        current_userid = get_jwt_identity()
        current_user = UserModel.find_by_id(ObjectId(current_userid))
        if not current_user:
            return {"message": "Current user not found"}, 403

        spotify_access_token = request.headers.get('spotify_access_token')
        if not spotify_access_token:
            return {"message": "header with spotify_access_token is missing"}, 400

        create_playlist_response = cls.create_playlist_in_spotify(current_user.spotify_id, data, spotify_access_token)
        spotify_playlist_id = create_playlist_response.data['id']

        cls.add_tracks_to_spotify_playlist(spotify_playlist_id, event.playlist, spotify_access_token)

        return {"message": "Playlist was imported to your spotify"}, 200

    @classmethod
    def create_playlist_in_spotify(cls, user_spotify_id, data, spotify_access_token):
        request_body = {'name': data['playlist_name'], 'description': data['description'], 'public': data['public']}
        create_playlist_response = spotify.post('users/' + user_spotify_id + '/playlists', data=request_body, format='json', token=spotify_access_token)
        return create_playlist_response

    @classmethod
    def add_tracks_to_spotify_playlist(cls, spotify_playlist_id, playlist, spotify_access_token):
        track_uris = ''.join(list(map(lambda track_id: 'spotify:track:' + track_id + ',', playlist)))
        url = 'https://api.spotify.com/v1/playlists/' + spotify_playlist_id + '/tracks?uris=' + track_uris
        spotify.post(url, format=None, token=spotify_access_token)
