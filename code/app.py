from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api

from config.bcrypt import bcrypt
from config.db import db, DevelopmentConfig
from properties import APP_SECRET_KEY
from resources.spotify_login import SpotifyLogin, SpotifyAuthorize
from resources.user import UserRegister, User, UserLogin

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = APP_SECRET_KEY
api = Api(app)
jwt = JWTManager(app)


api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(SpotifyLogin, "/login/spotify")
api.add_resource(SpotifyAuthorize, "/login/spotify/authorized", endpoint="spotify.authorize")

if __name__ == "__main__":
    db.init_app(app)
    bcrypt.init_app(app)
    app.run(port=5000, debug=True)
