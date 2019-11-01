from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_get_blocks():
    db = GathererDb(host='mongo')

    data = {
        'blocks': db.get_blocks()
    }

    return create_response(data=data)
