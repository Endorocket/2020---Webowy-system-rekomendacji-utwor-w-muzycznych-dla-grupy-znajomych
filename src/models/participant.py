from config.db import db
from models.user import UserModel


class ParticipantModel(db.EmbeddedDocument):
    user_id = db.ObjectIdField()
    role = db.StringField()

    def json(self, user: UserModel = None):
        return {
            'user_id': str(self.user_id),
            'role': self.role,
            'user': 'hidden' if user is None else user.json()
        }
