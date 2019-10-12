from helpers import create_response
from mongo import MongoMagic


def route_types():
    mongo = MongoMagic(host='mongo')

    data = {
        'types': [x for x in mongo.get_types()]
    }

    return create_response(data=data)
