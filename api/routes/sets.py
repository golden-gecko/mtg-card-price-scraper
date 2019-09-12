from helpers import create_response
from mongo import MongoMagic


def route_sets():
    mongo = MongoMagic(host='mongo')

    data = {
        'sets': [x for x in mongo.get_sets()]
    }

    return create_response(code=200, data=data)
