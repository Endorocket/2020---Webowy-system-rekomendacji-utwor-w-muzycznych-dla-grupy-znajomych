import datetime

import bson
from flask_jwt_extended import create_access_token
from flask_restful import Resource, reqparse

from config.bcrypt import bcrypt
from models.user import UserModel


class User(Resource):
    @classmethod
    def get(cls, user_id: str):
        user: UserModel = UserModel.find_by_id(bson.ObjectId(user_id))
        if not user:
            return {"message": "User not found."}, 404

        return user.json(), 200

    @classmethod
    def delete(cls, user_id: str):
        user: UserModel = UserModel.find_by_id(bson.ObjectId(user_id))
        if not user:
            return {"message": "User not found."}, 404

        user.delete_from_db()
        return {"message": "User deleted."}, 200


class UserRegister(Resource):
    @classmethod
    def post(cls):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help="This field cannot be left blank!")
        parser.add_argument('email', type=str, required=True, help="This field cannot be left blank!")
        parser.add_argument('password', type=str, required=True, help="This field cannot be left blank!")
        parser.add_argument('avatar_url', type=str, required=False)
        data = parser.parse_args()

        user = UserModel(username=data['username'], email=data['email'], password=data['password'],
                         avatar_url=data['avatar_url'])

        if UserModel.find_by_username(user.username):
            return {"message": "A user with that username already exists."}, 400

        if UserModel.find_by_email(user.email):
            return {"message": "A user with that email already exists."}, 400

        pw_hash = bcrypt.generate_password_hash(user.password).decode('utf-8')
        user.password = pw_hash

        user.save_to_db()

        return {"message": "Account created successfully."}, 201


class UserLogin(Resource):
    @classmethod
    def post(cls):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help="This field cannot be left blank!")
        parser.add_argument('password', type=str, required=True, help="This field cannot be left blank!")
        data = parser.parse_args()

        user: UserModel = UserModel.find_by_email(data['email'])

        if user and user.password and bcrypt.check_password_hash(user.password, data['password']):
            expires = datetime.timedelta(days=7)
            access_token = create_access_token(identity=str(user.id), fresh=True, expires_delta=expires)
            return {"access_token": access_token}, 200

        return {"message": "Invalid credentials!"}, 401
