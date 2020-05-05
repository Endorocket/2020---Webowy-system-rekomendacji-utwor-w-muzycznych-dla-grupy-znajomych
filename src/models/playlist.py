from config.db import db


class PlaylistModel(db.EmbeddedDocument):
    song_ids = db.ListField(db.StringField())
    duration_time = db.IntField()

    def json(self):
        return {
            'song_ids': list(self.song_ids),
            'duration_time': self.duration_time
        }