from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_get_artists():
    db = GathererDb()

    data = {
        'artists': db.get_artists()
    }

    return create_response(data=data)
