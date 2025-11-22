from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_get_colors():
    db = GathererDb()

    data = {
        'colors': db.get_colors()
    }

    return create_response(data=data)
