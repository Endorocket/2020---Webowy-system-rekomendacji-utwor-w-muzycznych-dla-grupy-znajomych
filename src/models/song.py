import bson

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

    def json(self):
        return {
            'track_id': self.track_id,
            'name': self.name,
            'album': self.invitation_link,
            'artist': self.artist,
            'genres': self.genres,
            'duration': self.duration,
            'image_url': self.image_url,
        }

    @classmethod
    def find_by_id(cls, track_id: bson.ObjectId) -> "SongModel":
        return cls.objects(track_id=track_id).first()

    @classmethod
    def find_all_genres(cls) -> list[str]:
        return cls.objects().distinct("genres")

    @classmethod
    def random_from_genre(cls, genre: str) -> "SongModel":
        song_list = cls.objects().aggregate([
                    { "$match": { "genres": genre } },
                    { "$sample": { "size": 1 } }
                ])

        return song_list[0]


    def save_to_db(self) -> None:
        self.save()




