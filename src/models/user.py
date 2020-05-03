from typing import List

from bson import ObjectId
from config.db import db


class UserModel(db.Document):
    username = db.StringField(required=True, unique=True)
    email = db.StringField(required=True, unique=True)
    password = db.StringField()
    avatar_url = db.StringField()
    pref_genres = db.ListField(db.StringField())

    song_ids = db.ListField(db.StringField())

    meta = {
        'collection': 'users',
        'indexes': [
            'username',
            'email'
        ]
    }

    def json(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'pref_genres': list(self.pref_genres)
        }

    @classmethod
    def find_by_id(cls, _id: ObjectId) -> "UserModel":
        return cls.objects(id=_id).first()

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.objects(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.objects(email=email).first()

    def save_to_db(self) -> None:
        self.save()

    def delete_from_db(self) -> None:
        self.delete()

    @classmethod
    def find_all_by_ids(cls, ids: List[ObjectId]) -> List["UserModel"]:
        return list(cls.objects(id__in=ids))
