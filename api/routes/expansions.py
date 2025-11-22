from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_expansions():
    db = GathererDb(host='mongo')

    data = {
        'expansions': db.get_expansions()
    }

    return create_response(data=data)
