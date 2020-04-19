from os import environ

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api

from config.bcrypt import bcrypt
from config.db import db, DevelopmentConfig, LocalConfig
from resources.event import Event, CreateEvent, EventList
from resources.invitation import InvitationByUsername, JoinByLink
from resources.spotify_login import SpotifyLogin, SpotifyAuthorize
from resources.user import UserRegister, User, UserLogin

app = Flask(__name__)
is_cloud = environ.get('IS_HEROKU', None)

if is_cloud:
    app.config.from_object(DevelopmentConfig)
else:
    app.config.from_object(LocalConfig)

app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = environ.get('APP_SECRET_KEY')
api = Api(app)
jwt = JWTManager(app)

api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(SpotifyLogin, "/login/spotify")
api.add_resource(SpotifyAuthorize, "/login/spotify/authorized", endpoint="spotify.authorize")
api.add_resource(Event, "/event/<event_id>")
api.add_resource(EventList, "/events")
api.add_resource(CreateEvent, "/event")
api.add_resource(InvitationByUsername, "/invite-to-event/<event_id>")
api.add_resource(JoinByLink, "/join-event")

if __name__ == "__main__":
    db.init_app(app)
    bcrypt.init_app(app)
    app.run(port=5000, debug=True)
