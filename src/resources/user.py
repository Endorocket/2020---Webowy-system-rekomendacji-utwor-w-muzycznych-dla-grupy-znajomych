import datetime
from typing import List

from bson import ObjectId
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse

from config.bcrypt import bcrypt
from enums.role import Role
from models.event import EventModel
from models.user import UserModel


class User(Resource):
    @classmethod
    def get(cls, user_id: str):
        if not ObjectId.is_valid(user_id):
            return {"message": "Id is not valid ObjectId"}, 400

        user: UserModel = UserModel.find_by_id(ObjectId(user_id))
        if not user:
            return {"message": "User not found."}, 404

        return user.json(), 200

    @classmethod
    @jwt_required
    def delete(cls, user_id: str):
        if not ObjectId.is_valid(user_id):
            return {"message": "Id is not valid ObjectId"}, 400

        current_userid = get_jwt_identity()
        if current_userid != user_id:
            return {"message": "Wrong user_id"}, 403

        current_user = UserModel.find_by_id(ObjectId(current_userid))
        if not current_user:
            return {"message": "Current user not found"}, 403

        current_user.delete_from_db()

        events: List[EventModel] = EventModel.find_all_by_admin_id(admin_id=current_user.id)
        for event in events:
            if len(list(filter(lambda participant: participant.role == Role.ADMIN, event.participants))) == 1:
                event.delete()

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
