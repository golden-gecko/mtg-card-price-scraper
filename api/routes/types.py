from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_types():
    db = GathererDb(host='mongo')

    data = {
        'types': [x for x in db.get_types()]
    }

    return create_response(data=data)
