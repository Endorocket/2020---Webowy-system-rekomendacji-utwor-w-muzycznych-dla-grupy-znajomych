from config.db import db


class SongModel(db.Document):
    track_id = db.StringField(primary_key=True)
    name = db.StringField()
    album = db.StringField()
    artist = db.StringField()
    genres = db.ListField(db.StringField())
    duration = db.IntField()
    image_url = db.StringField()

    meta = {
        'collection': 'songs'
    }
