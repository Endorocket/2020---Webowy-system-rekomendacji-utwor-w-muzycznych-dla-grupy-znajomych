from config.db import db
from models.participant import ParticipantModel
from models.playlist import PlaylistModel


class EventModel(db.Document):
    name = db.StringField(required=True)
    invitation_link = db.StringField()
    date = db.DateTimeField()
    frequency = db.StringField()
    duration_time = db.IntField()
    image_url = db.StringField()

    playlist = db.EmbeddedDocumentField(PlaylistModel)
    participants = db.EmbeddedDocumentListField(ParticipantModel, required=True)

    meta = {
        'collection': 'events',
        'indexes': [
            'participants.user_id'
        ]
    }
