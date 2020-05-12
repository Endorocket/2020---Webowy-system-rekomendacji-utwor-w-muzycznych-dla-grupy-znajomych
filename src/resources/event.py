import uuid
from datetime import datetime
from typing import List

from bson import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse

from enums.role import Role
from enums.status import Status
from models.event import EventModel
from models.participant import ParticipantModel
from models.user import UserModel
from ml.recommendation_algorithm import Recommendation_Algorithm_SVD


class Event(Resource):
    @classmethod
    def get(cls, event_id: str):
        if not ObjectId.is_valid(event_id):
            return {"status": Status.INVALID_FORMAT, "message": "Id is not valid ObjectId"}, 400

        event: EventModel = EventModel.find_by_id(ObjectId(event_id))
        if not event:
            return {"status": Status.NOT_FOUND, "message": "Event not found."}, 404

        participants_id = list(map(lambda participant: participant.user_id, event.participants))
        users: List[UserModel] = UserModel.find_all_by_ids(participants_id)

        return {"status": Status.SUCCESS, "event": event.json(users)}, 200

    @classmethod
    @jwt_required
    def put(cls, event_id: str):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=False)
        parser.add_argument('description', type=str, required=False)
        parser.add_argument('start_date', type=datetime.fromisoformat, required=False)
        parser.add_argument('end_date', type=datetime.fromisoformat, required=False)
        parser.add_argument('duration_time', type=int, required=False)
        parser.add_argument('image_url', type=str, required=False)
        data = parser.parse_args()

        if not ObjectId.is_valid(event_id):
            return {"status": Status.INVALID_FORMAT, "message": "Id is not valid ObjectId"}, 400

        current_userid = get_jwt_identity()
        current_user = UserModel.find_by_id(current_userid)
        if not current_user:
            return {"status": Status.USER_NOT_FOUND, "message": "Current user not found"}, 403

        event: EventModel = EventModel.find_by_id_and_admin_id(ObjectId(event_id), current_userid)
        if not event:
            return {"status": Status.NOT_FOUND, "message": "Event not found with admin as current user"}, 404

        if data['name']:
            if len(data['name']) < 3:
                return {"status": Status.INVALID_FORMAT, "message": "name must be at least 3 chars long"}, 400
            event.name = data['name']

        if data['description']:
            event.data = data['description']

        start_date: datetime = data['start_date']
        end_date: datetime = data['end_date']

        if start_date and end_date:
            if start_date > end_date:
                return {"status": Status.INVALID_DATA, "message": "End_date cannot be before start_date"}, 403
            event.start_date = start_date
            event.end_date = end_date
        elif end_date:
            if event.start_date and event.start_date > end_date:
                return {"status": Status.INVALID_DATA, "message": "End_date cannot be before start_date"}, 403
            event.end_date = end_date
        elif start_date:
            if event.end_date and event.end_date < start_date:
                return {"status": Status.INVALID_DATA, "message": "End_date cannot be before start_date"}, 403
            event.start_date = start_date

        duration_time = data['duration_time']
        if duration_time and duration_time < 0:
            return {"status": Status.INVALID_DATA, "message": "Duration_time cannot be less than 0"}, 403
        event.duration_time = duration_time

        if data['image_url']:
            event.image_url = data['image_url']

        event.save_to_db()

        return {"status": Status.SUCCESS, "event": event.json()}, 200

    @classmethod
    @jwt_required
    def delete(cls, event_id: str):
        if not ObjectId.is_valid(event_id):
            return {"status": Status.INVALID_FORMAT, "message": "Id is not valid ObjectId"}, 400

        current_userid = get_jwt_identity()
        current_user = UserModel.find_by_id(current_userid)
        if not current_user:
            return {"status": Status.USER_NOT_FOUND, "message": "Current user not found"}, 403

        event: EventModel = EventModel.find_by_id_and_admin_id(ObjectId(event_id), current_userid)
        if not event:
            return {"status": Status.NOT_FOUND, "message": "Event not found with admin as current user"}, 404

        event.delete()
        return {"status": Status.SUCCESS, "message": "Event deleted"}, 200


class EventList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        current_userid = get_jwt_identity()
        current_user = UserModel.find_by_id(ObjectId(current_userid))
        if not current_user:
            return {"status": Status.USER_NOT_FOUND, "message": "Current user not found"}, 403

        events: List[EventModel] = EventModel.find_all_by_participant_id(current_user.id)

        return {"status": Status.SUCCESS,
                "events": list(map(lambda event:
                                   event.json(UserModel.find_all_by_ids(list(map(lambda participant:
                                                                                 participant.user_id, event.participants)))), events))
                }, 200


class CreateEvent(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('description', type=str, required=False)
        parser.add_argument('start_date', type=datetime.fromisoformat, required=True)
        parser.add_argument('end_date', type=datetime.fromisoformat, required=True)
        parser.add_argument('duration_time', type=int, required=False)
        parser.add_argument('image_url', type=str, required=False)
        data = parser.parse_args()

        current_userid = get_jwt_identity()
        current_user = UserModel.find_by_id(current_userid)

        if not current_user:
            return {"status": Status.USER_NOT_FOUND, "message": "User not found"}, 403

        start_date: datetime = data['start_date']
        end_date: datetime = data['end_date']
        if start_date > end_date:
            return {"status": Status.INVALID_DATA, "message": "End_date cannot be before start_date"}, 403

        duration_time = data['duration_time']
        if duration_time and duration_time < 0:
            return {"status": Status.INVALID_DATA, "message": "Duration_time cannot be less than 0"}, 403

        event = EventModel(name=data['name'], description=data['description'], start_date=start_date, end_date=end_date, image_url=data['image_url'],
                           duration_time=duration_time)

        admin_participant = ParticipantModel(user_id=current_user.id, role=Role.ADMIN)
        event.participants.append(admin_participant)

        event.invitation_link = str(uuid.uuid4())

        event.save_to_db()

        return {"status": Status.SUCCESS,
                "message": "Event created successfully",
                "event": event.json()
                }, 201


class CreatePlaylist(Resource):
    @classmethod
    @jwt_required
    def get(cls, event_id: str):

        event: EventModel = EventModel.find_by_id(ObjectId(event_id))

        current_user_id = get_jwt_identity()

        for participant in event.participants:
            if current_user_id == participant.user_id:
                if participant.role == Role.ADMIN:
                    song_ids = Recommendation_Algorithm_SVD(event_id)
                    event.playlist = song_ids
                    event.save_to_db()

                    return {"status": Status.SUCCESS, "event": event.json()}, 200
                else:
                    return {"status": Status.NO_ADMIN, "message": "User is not an admin"}, 403

        return {"status": Status.USER_NOT_FOUND, "message": "User is not event participant"}, 403
