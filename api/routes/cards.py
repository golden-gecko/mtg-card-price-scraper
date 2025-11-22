from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_cards():
    db = GathererDb(host='mongo')

    data = {
        'cards': [x for x in db.get_cards()]
    }

    return create_response(data=data)
