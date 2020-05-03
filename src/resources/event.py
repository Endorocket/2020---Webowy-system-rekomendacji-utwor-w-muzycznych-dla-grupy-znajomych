import uuid
from datetime import datetime
from typing import List

from bson import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse

from enums.role import Role
from models.event import EventModel
from models.participant import ParticipantModel
from models.user import UserModel


class Event(Resource):
    @classmethod
    def get(cls, event_id: str):
        if not ObjectId.is_valid(event_id):
            return {"message": "Id is not valid ObjectId"}, 400

        event: EventModel = EventModel.find_by_id(ObjectId(event_id))
        if not event:
            return {"message": "Event not found."}, 404

        return event.json(), 200


class EventList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        current_userid = get_jwt_identity()
        current_user = UserModel.find_by_id(ObjectId(current_userid))
        if not current_user:
            return {"message": "Current user not found"}, 403

        events: List[EventModel] = EventModel.find_all_by_participant_id(current_user.id)

        return {'events': list(map(lambda event: event.json(), events))}


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
            return {"message": "User not found"}, 403

        start_date: datetime = data['start_date']
        end_date: datetime = data['end_date']
        if start_date > end_date:
            return {"message": "End_date cannot be before start_date"}, 403

        duration_time = data['duration_time']
        if duration_time < 0:
            return {"message": "Duration_time cannot be less than 0"}, 403

        event = EventModel(name=data['name'], description=data['description'], start_date=start_date, end_date=end_date, image_url=data['image_url'],
                           duration_time=duration_time)

        admin_participant = ParticipantModel(user_id=current_user.id, role=Role.ADMIN)
        event.participants.append(admin_participant)

        event.invitation_link = str(uuid.uuid4())

        event.save_to_db()

        return {"message": "Event created successfully."}, 201
