from helpers import create_response
from mongo import MongoMagic


def route_formats():
    mongo = MongoMagic(host='mongo')

    data = {
        'formats': [x for x in mongo.get_formats()]
    }

    return create_response(data=data)
