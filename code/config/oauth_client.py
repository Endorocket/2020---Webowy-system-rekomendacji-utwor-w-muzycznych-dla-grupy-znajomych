from os import environ

from flask_oauthlib.client import OAuth

from config.scope import scope

oauth = OAuth()

spotify = oauth.remote_app(
    'spotify',
    consumer_key=environ.get('CONSUMER_KEY'),
    consumer_secret=environ.get('CONSUMER_SECRET'),
    request_token_params={"scope": scope},
    base_url="https://api.spotify.com/v1/",
    request_token_url=None,
    access_token_method="POST",
    access_token_url="https://accounts.spotify.com/api/token",
    authorize_url="https://accounts.spotify.com/authorize"
)
