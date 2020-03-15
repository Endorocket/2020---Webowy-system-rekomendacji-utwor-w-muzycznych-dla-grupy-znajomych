from flask import url_for, request
from flask_jwt_extended import create_access_token
from flask_restful import Resource

from models.user import UserModel
from config.oauth_client import spotify


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
        spotify_refresh_token = response['refresh_token']

        # TODO - save tokens in session?

        spotify_user = spotify.get('me', token=spotify_access_token)
        spotify_email = spotify_user.data['email']

        user = UserModel.find_by_email(spotify_email)

        if not user:
            user = UserModel(email=spotify_email, password=None)
            user.save_to_db()

        access_token = create_access_token(identity=user.id, fresh=True)

        return {"access_token": access_token}
