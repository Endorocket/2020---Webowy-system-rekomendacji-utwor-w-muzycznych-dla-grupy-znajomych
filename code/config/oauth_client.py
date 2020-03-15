from flask_oauthlib.client import OAuth

from config.scope import scope
from properties import CONSUMER_KEY, CONSUMER_SECRET

oauth = OAuth()

spotify = oauth.remote_app(
    'spotify',
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    request_token_params={"scope": scope},
    base_url="https://api.spotify.com/v1/",
    request_token_url=None,
    access_token_method="POST",
    access_token_url="https://accounts.spotify.com/api/token",
    authorize_url="https://accounts.spotify.com/authorize"
)
