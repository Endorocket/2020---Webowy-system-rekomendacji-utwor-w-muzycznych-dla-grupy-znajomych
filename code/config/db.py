from flask_mongoengine import MongoEngine

db = MongoEngine()


class DevelopmentConfig:
    MONGODB_SETTINGS = {
        'db': 'music',
        'host': '127.0.0.1',
        'port': 27017
    }
