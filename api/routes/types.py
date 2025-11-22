from helpers import create_response
from mongo import Mongo


def route_types():
    mongo = Mongo(host='mongo')

    data = {
        'types': [x for x in mongo.get_types()]
    }

    return create_response(code=200, data=data)
