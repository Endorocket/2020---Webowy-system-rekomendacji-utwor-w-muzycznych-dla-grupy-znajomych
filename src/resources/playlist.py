from bson import ObjectId
from flask import request
from flask_api import status
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource, reqparse

from config.oauth_client import spotify
from enums.role import Role
from enums.status import Status
from ml.recommendation_algorithm import RecommendationAlgorithmSVD
from models.event import EventModel
from models.user import UserModel


class CreatePlaylist(Resource):
    @classmethod
    @jwt_required
    def post(cls, event_id: str):

        event: EventModel = EventModel.find_by_id(ObjectId(event_id))

        current_user_id = get_jwt_identity()

        for participant in event.participants:
            if str(current_user_id) == str(participant.user_id):
                if participant.role == Role.ADMIN:
                    event_json = RecommendationAlgorithmSVD.run(event_id)

                    return {"status": Status.SUCCESS, "event": event_json}, 200
                else:
                    return {"status": Status.NO_ADMIN, "message": "User is not an admin"}, 403

        return {"status": Status.USER_NOT_FOUND, "message": "User is not event participant"}, 403


class ExportPlaylist(Resource):
    @classmethod
    @jwt_required
    def post(cls, event_id: str):
        parser = reqparse.RequestParser()
        parser.add_argument('playlist_name', type=str, required=True)
        parser.add_argument('description', type=str, required=True)
        parser.add_argument('public', type=str, default='false', choices=('true', 'false'))
        parser.add_argument('spotify_access_token', type=str, required=True)
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

        spotify_access_token = data['spotify_access_token']
        create_playlist_response = cls.create_playlist_in_spotify(current_user.spotify_id, data, spotify_access_token)

        if not status.is_success(create_playlist_response.status):
            return {"status": Status.INVALID_SPOTIFY_TOKEN, "spotify_error": create_playlist_response.data['error']}, 400

        spotify_playlist_id = create_playlist_response.data['id']

        size_of_chunk = 20
        playlist_size = len(event.playlist)
        playlist_chunks = [event.playlist[i:i + size_of_chunk] for i in range(0, playlist_size, size_of_chunk)]

        for playlist_chunk in playlist_chunks:
            add_tracks_response = cls.add_tracks_to_spotify_playlist(spotify_playlist_id, playlist_chunk, spotify_access_token)

            if not status.is_success(add_tracks_response.status):
                return {"status": Status.INVALID_SPOTIFY_TOKEN, "spotify_error": add_tracks_response.data['error']}, 400

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
