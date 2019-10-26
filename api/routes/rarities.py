from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_rarities():
    db = GathererDb(host='mongo')

    data = {
        'rarities': db.get_rarities()
    }

    return create_response(data=data)
