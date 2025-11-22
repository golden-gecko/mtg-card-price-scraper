from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_get_formats():
    db = GathererDb()

    data = {
        'formats': db.get_formats()
    }

    return create_response(data=data)
