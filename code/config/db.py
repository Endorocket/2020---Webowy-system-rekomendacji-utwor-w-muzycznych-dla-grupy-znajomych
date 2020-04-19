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
        'host': 'mongodb://heroku_3lvj3gxj:pn36um10djp0di4p8dcguoulp0@ds235437.mlab.com:35437/heroku_3lvj3gxj?retryWrites=false'
    }
