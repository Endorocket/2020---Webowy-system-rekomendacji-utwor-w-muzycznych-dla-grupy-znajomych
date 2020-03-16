from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource

from config.bcrypt import bcrypt
from models.user import UserModel
from schemas.user import UserSchema

user_schema = UserSchema()


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user: UserModel = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found."}, 404

        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user: UserModel = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found."}, 404

        user.delete_from_db()
        return {"message": "User deleted."}, 200


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user: UserModel = user_schema.load(user_json)

        if UserModel.find_by_email(user.email):
            return {"message": "A user with that email already exists."}, 400

        pw_hash = bcrypt.generate_password_hash(user.password)
        user.password = pw_hash

        user.save_to_db()

        return {"message": "Account created successfully."}, 201


class UserLogin(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user_data = user_schema.load(user_json)

        user: UserModel = UserModel.find_by_email(user_data.email)

        if user and user.password and bcrypt.check_password_hash(user.password, user_data.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            return {"access_token": access_token}, 200

        return {"message": "Invalid credentials!"}, 401
