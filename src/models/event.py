from typing import List, Dict

import bson

from config.db import db
from enums.role import Role
from models.participant import ParticipantModel
from models.user import UserModel
from models.song import SongModel


class EventModel(db.Document):
    name = db.StringField(required=True)
    description = db.StringField()
    invitation_link = db.StringField()
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    duration_time = db.IntField()
    image_url = db.StringField()

    playlist = db.ListField(db.StringField())
    participants = db.EmbeddedDocumentListField(ParticipantModel, required=True)

    meta = {
        'collection': 'events',
        'indexes': [
            'invitation_link',
            'participants.user_id'
        ]
    }

    def json(self, users: List[UserModel] = None) -> Dict:
        users_dict = {user.id: user for user in users} if users else None
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'invitation_link': self.invitation_link,
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'duration_time': self.duration_time,
            'image_url': self.image_url,
            'playlist': self.playlist if len(self.playlist) > 0 else [],
            'participants': list(map(lambda participant: participant.json(), self.participants)) if users is None
            else list(map(lambda participant: participant.json(users_dict[participant.user_id]), self.participants))
        }
    def json2(self, songs: List[SongModel], users: List[UserModel] = None) -> Dict:
        users_dict = {user.id: user for user in users} if users else None
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'invitation_link': self.invitation_link,
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'duration_time': self.duration_time,
            'image_url': self.image_url,
            'playlist': songs if len(songs) > 0 else [],
            'participants': list(map(lambda participant: participant.json(), self.participants)) if users is None
            else list(map(lambda participant: participant.json(users_dict[participant.user_id]), self.participants))
        }

    @classmethod
    def find_by_id(cls, _id: bson.ObjectId) -> "EventModel":
        return cls.objects(id=_id).first()

    @classmethod
    def find_by_id_and_admin_id(cls, _id: bson.ObjectId, admin_id: bson.ObjectId) -> "EventModel":
        return cls.objects(id=_id, participants__user_id=admin_id, participants__role=Role.ADMIN).first()

    @classmethod
    def find_by_invitation_link(cls, invitation_link: str) -> "EventModel":
        return cls.objects(invitation_link=invitation_link).first()

    @classmethod
    def find_all_by_participant_id(cls, user_id: bson.ObjectId) -> List["EventModel"]:
        return list(cls.objects(participants__user_id=user_id))

    @classmethod
    def find_all_by_admin_id(cls, admin_id: bson.ObjectId) -> List["EventModel"]:
        return list(cls.objects(participants__user_id=admin_id, participants__role=Role.ADMIN))

    def add_new_participant(self, user_id: bson.ObjectId) -> bool:
        new_participant = ParticipantModel(user_id=user_id, role=Role.MEMBER)
        result = self.update(push__participants=new_participant)
        return result == 1

    def remove_participant(self, user_id: bson.ObjectId) -> bool:
        result = self.update(pull__participants__user_id=user_id)
        return result == 1

    def save_to_db(self) -> None:
        self.save()
