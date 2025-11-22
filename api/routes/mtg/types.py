from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_get_types():
    db = GathererDb(host='mongo')

    data = {
        'types': db.get_types()
    }

    return create_response(data=data)
