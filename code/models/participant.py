from config.db import db


class ParticipantModel(db.EmbeddedDocument):
    user_id = db.ObjectIdField()
    role = db.StringField()
