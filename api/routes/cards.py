from helpers import create_response
from mongo import MongoMagic


def route_cards():
    mongo = MongoMagic(host='mongo')

    data = {
        'cards': [x for x in mongo.get_cards()]
    }

    return create_response(data=data)
