from typing import List

from config.db import db


class SongModel(db.Document):
    track_id = db.StringField(primary_key=True)
    name = db.StringField()
    album = db.StringField()
    artist = db.ListField(db.StringField())
    genres = db.ListField(db.StringField())
    duration = db.IntField()
    image_url = db.StringField()

    meta = {
        'collection': 'songs',
        'indexes': [
            'genres'
        ]
    }

    def json(self):
        return {
            'track_id': self.track_id,
            'name': self.name,
            'album': self.album,
            'artist': self.artist,
            'genres': self.genres,
            'duration': self.duration,
            'image_url': self.image_url,
        }

    @classmethod
    def find_by_id(cls, track_id: str) -> "SongModel":
        return cls.objects(track_id=track_id).first()

    @classmethod
    def find_all_genres(cls) -> List[str]:
        return list(cls.objects().distinct("genres"))

    @classmethod
    def random_from_genre(cls, genre: str) -> "SongModel":
        song_list = list(cls.objects().aggregate([
            {"$match": {"genres": genre}},
            {"$sample": {"size": 1}}
        ]))

        return cls.objects(track_id=song_list[0]['_id']).first()

    @classmethod
    def random_from_genres(cls, genres: dict) -> List["SongModel"]:
        song_list = []
        for key in genres:
            song_list += list(cls.objects().aggregate([
                {"$match": {"genres": key}},
                {"$sample": {"size": genres[key]}}
            ]))

        return song_list

    @classmethod
    def find_top_genres(cls, quantity: int) -> List[str]:
        return list(cls.objects().aggregate([
            {"$unwind": "$genres"},
            {"$group": {
                "_id": "$genres",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": quantity}
        ]))

    def save_to_db(self) -> None:
        self.save()
