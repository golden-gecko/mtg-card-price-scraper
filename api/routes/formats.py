from helpers import create_response
from mongo import Mongo


def route_formats():
    mongo = Mongo(host='mongo')

    data = {
        'formats': [x for x in mongo.get_formats()]
    }

    return create_response(code=200, data=data)
