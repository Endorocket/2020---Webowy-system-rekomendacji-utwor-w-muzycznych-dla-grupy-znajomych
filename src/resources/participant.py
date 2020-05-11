from bson import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse

from enums.role import Role
from enums.status import Status
from models.event import EventModel
from models.participant import ParticipantModel
from models.user import UserModel


class InvitationByUsername(Resource):
    @classmethod
    @jwt_required
    def post(cls, event_id: str):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        data = parser.parse_args()

        if not ObjectId.is_valid(event_id):
            return {"status": Status.INVALID_FORMAT, "message": "Id is not valid ObjectId"}, 400

        current_userid = get_jwt_identity()
        current_user = UserModel.find_by_id(ObjectId(current_userid))
        if not current_user:
            return {"status": Status.USER_NOT_FOUND, "message": "Current user not found"}, 403

        user_to_add = UserModel.find_by_username(data['username'])
        if not user_to_add:
            return {"status": Status.USER_NOT_FOUND, "message": "User you want to add not found"}, 403

        event = EventModel.find_by_id_and_admin_id(ObjectId(event_id), current_user.id)
        if not event:
            return {"status": Status.NO_ADMIN, "message": "Event with admin as current user not found"}, 403

        if len(list(filter(lambda participant: participant.user_id == user_to_add.id, event.participants))) > 0:
            return {"status": Status.DUPLICATED, "message": "User you want to add is already in event"}, 403

        is_success = event.add_new_participant(user_to_add.id)
        if not is_success:
            return {"status": Status.ERROR, "message": "Some error occured"}, 400

        return {"status": Status.SUCCESS, "message": "User joined event successfully"}, 200


class JoinByLink(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        parser = reqparse.RequestParser()
        parser.add_argument('invitation_link', type=str, required=True)
        data = parser.parse_args()

        current_userid = get_jwt_identity()
        current_user = UserModel.find_by_id(ObjectId(current_userid))
        if not current_user:
            return {"status": Status.USER_NOT_FOUND, "message": "User not found"}, 403

        invitation_link = data['invitation_link']
        event = EventModel.find_by_invitation_link(invitation_link)

        if event is None:
            return {"status": Status.INVALID_DATA, "message": "invitation_link was broken"}, 403

        if len(list(filter(lambda participant: participant.user_id == current_user.id, event.participants))) > 0:
            return {"status": Status.DUPLICATED, "message": "User you want to add is already in event"}, 403

        is_success = event.add_new_participant(current_user.id)
        if not is_success:
            return {"status": Status.ERROR, "message": "Some error occured"}, 400

        return {"status": Status.SUCCESS, "message": "User joined event successfully"}, 200


class RemoveUser(Resource):
    @classmethod
    @jwt_required
    def post(cls, event_id: str):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        data = parser.parse_args()

        if not ObjectId.is_valid(event_id):
            return {"status": Status.INVALID_FORMAT, "message": "Id is not valid ObjectId"}, 400

        current_userid = get_jwt_identity()
        current_user = UserModel.find_by_id(ObjectId(current_userid))
        if not current_user:
            return {"status": Status.USER_NOT_FOUND, "message": "Current user not found"}, 403

        user_to_remove = UserModel.find_by_username(data['username'])
        if not user_to_remove:
            return {"status": Status.USER_NOT_FOUND, "message": "User you want to add not found"}, 403

        event = EventModel.find_by_id_and_admin_id(ObjectId(event_id), current_user.id)
        if not event:
            return {"status": Status.USER_NOT_FOUND, "message": "Event with admin as current user not found"}, 403

        is_success = event.remove_participant(user_id=user_to_remove.id)
        if not is_success:
            return {"status": Status.ERROR, "message": "Some error occured"}, 400

        event.reload()
        if len(list(filter(lambda participant: participant.role == Role.ADMIN, event.participants))) == 0:
            event.delete()
            return {"status": Status.SUCCESS, "message": "Event removed because last admin was removed"}, 200

        return {"status": Status.SUCCESS, "message": "User removed from an event"}, 200


class GrantAdmin(Resource):
    @classmethod
    @jwt_required
    def post(cls, event_id: str):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        data = parser.parse_args()

        if not ObjectId.is_valid(event_id):
            return {"status": Status.INVALID_FORMAT, "message": "Id is not valid ObjectId"}, 400

        current_userid = get_jwt_identity()
        current_user = UserModel.find_by_id(ObjectId(current_userid))
        if not current_user:
            return {"status": Status.USER_NOT_FOUND, "message": "Current user not found"}, 403

        user_to_update = UserModel.find_by_username(data['username'])
        if not user_to_update:
            return {"status": Status.USER_NOT_FOUND, "message": "User you want to add not found"}, 403

        event = EventModel.find_by_id_and_admin_id(ObjectId(event_id), current_user.id)
        if not event:
            return {"status": Status.USER_NOT_FOUND, "message": "Event with admin as current user not found"}, 403

        participant_to_update: ParticipantModel = \
            next(filter(lambda participant: participant.user_id == user_to_update.id, event.participants), None)

        if not participant_to_update:
            return {"status": Status.USER_NOT_FOUND, "message": "User you want to grant admin is not in the event"}, 403

        participant_to_update.role = Role.ADMIN
        event.save()

        return {"status": Status.SUCCESS,
                "message": "Admin granted",
                "participant": participant_to_update.json()
                }, 200


class RevokeAdmin(Resource):
    @classmethod
    @jwt_required
    def post(cls, event_id: str):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        data = parser.parse_args()

        if not ObjectId.is_valid(event_id):
            return {"status": Status.INVALID_FORMAT, "message": "Id is not valid ObjectId"}, 400

        current_userid = get_jwt_identity()
        current_user = UserModel.find_by_id(ObjectId(current_userid))
        if not current_user:
            return {"status": Status.USER_NOT_FOUND, "message": "Current user not found"}, 403

        user_to_update = UserModel.find_by_username(data['username'])
        if not user_to_update:
            return {"status": Status.USER_NOT_FOUND, "message": "User you want to add not found"}, 403
        if user_to_update.id == current_user.id:
            return {"status": Status.INVALID_DATA, "message": "Cannot revoke admin to yourself"}, 403

        event = EventModel.find_by_id_and_admin_id(ObjectId(event_id), current_user.id)
        if not event:
            return {"status": Status.NO_ADMIN, "message": "Event with admin as current user not found"}, 403

        participant_to_update: ParticipantModel = next(
            filter(lambda participant: participant.user_id == user_to_update.id, event.participants), None)
        if not participant_to_update:
            return {"status": Status.USER_NOT_FOUND, "message": "User you want to revoke admin is not in the event"}, 403

        participant_to_update.role = Role.MEMBER
        event.save()

        return {"status": Status.SUCCESS,
                "message": "Admin revoked",
                "participant": participant_to_update.json()
                }, 200
