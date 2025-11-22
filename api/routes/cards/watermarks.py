from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_get_watermarks():
    db = GathererDb()

    data = {
        'watermarks': db.get_watermarks()
    }

    return create_response(data=data)
