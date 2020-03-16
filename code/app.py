from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_restful import Api
from marshmallow import ValidationError

from config.bcrypt import bcrypt
from config.db import db
from config.ma import ma
from properties import APP_SECRET_KEY
from resources.spotify_login import SpotifyLogin, SpotifyAuthorize
from resources.user import UserRegister, User, UserLogin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = APP_SECRET_KEY
api = Api(app)
jwt = JWTManager(app)


@app.before_first_request
def create_tables():
    db.create_all()


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(SpotifyLogin, "/login/spotify")
api.add_resource(SpotifyAuthorize, "/login/spotify/authorized", endpoint="spotify.authorize")

if __name__ == "__main__":
    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    app.run(port=5000, debug=True)
