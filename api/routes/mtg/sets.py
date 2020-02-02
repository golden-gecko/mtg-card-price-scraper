from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_get_sets():
    db = GathererDb()

    data = {
        'sets': db.get_sets()
    }

    return create_response(data=data)
