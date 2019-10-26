from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_colors():
    db = GathererDb(host='mongo')

    data = {
        'colors': db.get_colors()
    }

    return create_response(data=data)
