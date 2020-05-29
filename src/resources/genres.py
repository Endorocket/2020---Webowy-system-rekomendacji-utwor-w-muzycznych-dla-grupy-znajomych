from flask_restful import Resource
from models.song import SongModel
from enums.status import Status


class TopGenres(Resource):
    @classmethod
    def get(cls, quantity: str):
        try:
            genres = ['classical','rock','pop','edm','hip hop',
                      'electronica','blues','soundtrack','r&b','jazz',
                      'metal','house','disco','country','latin',
                      'christian music','indie rock','synthpop','eurodance','folk']
            top_genres = {'genres': genres[:int(quantity)]}
            return top_genres
        except ValueError:
            return {"status": Status.INVALID_FORMAT, "message": "Value is not an integer"}, 400
