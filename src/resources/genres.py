from flask_restful import Resource,reqparse
from models.song import SongModel
import json

class TopGenres(Resource):
    @classmethod
    def get(cls, quantity: str):
        top_genres = {'genres':[x['_id'] for x in SongModel.find_top_genres(int(quantity))]}
        return top_genres
