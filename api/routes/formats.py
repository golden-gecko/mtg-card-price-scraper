from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_formats():
    db = GathererDb(host='mongo')

    data = {
        'formats': [x for x in db.get_formats()]
    }

    return create_response(data=data)
