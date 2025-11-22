from helpers import create_response
from mongo import Mongo


def route_cards():
    mongo = Mongo(host='mongo')

    data = {
        'cards': [x for x in mongo.get_cards()]
    }

    return create_response(code=200, data=data)
