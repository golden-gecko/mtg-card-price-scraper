from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_sets():
    db = GathererDb(host='mongo')

    data = {
        'sets': [x for x in db.get_sets()]
    }

    return create_response(data=data)
