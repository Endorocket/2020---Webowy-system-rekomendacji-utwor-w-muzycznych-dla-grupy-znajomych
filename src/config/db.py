from os import environ

from flask_mongoengine import MongoEngine

db = MongoEngine()


class LocalConfig:
    MONGODB_SETTINGS = {
        'db': 'music',
        'host': '127.0.0.1',
        'port': 27017
    }


class DevelopmentConfig:
    MONGODB_SETTINGS = {
        'host': environ.get('MONGODB_URI'),
        'connect': False
    }
