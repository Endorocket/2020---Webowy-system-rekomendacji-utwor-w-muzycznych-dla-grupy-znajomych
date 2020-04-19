from config.db import db


class ParticipantModel(db.EmbeddedDocument):
    user_id = db.ObjectIdField()
    role = db.StringField()

    def json(self):
        return {
            'user_id': str(self.user_id),
            'role': self.role
        }
