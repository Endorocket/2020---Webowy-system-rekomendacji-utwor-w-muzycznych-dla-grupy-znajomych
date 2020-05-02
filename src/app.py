from os import environ

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_cors import CORS

from config.bcrypt import bcrypt
from config.db import db, DevelopmentConfig, LocalConfig
from resources.event import Event, CreateEvent, EventList
from resources.participant import InvitationByUsername, JoinByLink, RemoveUser, GrantAdmin, RevokeAdmin
from resources.spotify_login import SpotifyLogin, SpotifyAuthorize
from resources.user import UserRegister, User, UserLogin, UserCurrent

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
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

api.add_resource(UserRegister, "/api/register")
api.add_resource(UserLogin, "/api/login")
api.add_resource(User, "/api/user/<user_id>")
api.add_resource(UserCurrent, "/api/user/current")
api.add_resource(SpotifyLogin, "/api/login/spotify")
api.add_resource(SpotifyAuthorize, "/api/login/spotify/authorized", endpoint="spotify.authorize")
api.add_resource(Event, "/api/event/<event_id>")
api.add_resource(EventList, "/api/events")
api.add_resource(CreateEvent, "/api/event")
api.add_resource(InvitationByUsername, "/api/event/<event_id>/invite")
api.add_resource(RemoveUser, "/api/event/<event_id>/remove-user")
api.add_resource(GrantAdmin, "/api/event/<event_id>/grant-admin")
api.add_resource(RevokeAdmin, "/api/event/<event_id>/revoke-admin")
api.add_resource(JoinByLink, "/api/join-event")

db.init_app(app)
bcrypt.init_app(app)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
