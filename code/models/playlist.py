from config.db import db


class PlaylistModel(db.EmbeddedDocument):
    song_ids = db.ListField(db.StringField())
    duration_time = db.IntField()
