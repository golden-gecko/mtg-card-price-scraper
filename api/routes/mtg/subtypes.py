from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_get_subtypes():
    db = GathererDb(host='mongo')

    data = {
        'subtypes': db.get_subtypes()
    }

    return create_response(data=data)
