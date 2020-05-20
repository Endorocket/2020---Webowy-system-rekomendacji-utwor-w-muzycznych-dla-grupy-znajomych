from flask_restful import Resource,reqparse
from models.song import SongModel
from enums.status import Status
import json

class TopGenres(Resource):
    @classmethod
    def get(cls, quantity: str):
        try:
            top_genres = {'genres':[x['_id'] for x in SongModel.find_top_genres(int(quantity))]}
            return top_genres
        except ValueError:
            return {"status": Status.INVALID_FORMAT, "message": "Value is not an integer"}, 400
