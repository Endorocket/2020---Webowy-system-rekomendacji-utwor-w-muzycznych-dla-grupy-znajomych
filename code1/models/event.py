import bson

from typing import List

from config.db import db
from enums.frequency import Frequency
from enums.role import Role
from models.participant import ParticipantModel
from models.playlist import PlaylistModel


class EventModel(db.Document):
    name = db.StringField(required=True)
    invitation_link = db.StringField()
    date = db.DateTimeField()
    frequency = db.StringField(choices=(Frequency.ONCE, Frequency.WEEK, Frequency.MONTH))
    duration_time = db.IntField()
    image_url = db.StringField()

    playlist = db.EmbeddedDocumentField(PlaylistModel)
    participants = db.EmbeddedDocumentListField(ParticipantModel, required=True)

    meta = {
        'collection': 'events',
        'indexes': [
            'invitation_link',
            'participants.user_id'
        ]
    }

    def json(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'invitation_link': self.invitation_link,
            'date': str(self.date),
            'frequency': self.frequency,
            'duration_time': self.duration_time,
            'image_url': self.image_url,
            'playlist': list(map(lambda playlist: playlist.json(), self.playlist)) if self.playlist else [],
            'participants': list(map(lambda participant: participant.json(), self.participants))
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
    def add_new_participant(cls, _id: bson.ObjectId, user_id: bson.ObjectId) -> bool:
        new_participant = ParticipantModel(user_id=user_id, role=Role.MEMBER)

        result = cls.objects(id=_id).update_one(push__participants=new_participant)
        return result == 1

    def save_to_db(self) -> None:
        self.save()
