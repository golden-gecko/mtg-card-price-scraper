from flask import request

from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_get_cards():
    db = GathererDb(host='mongo')

    cards = db.get_cards(
        name=request.args.get('name', default=''),
        page=request.args.get('page', default=0, type=int),
        limit=request.args.get('limit', default=12, type=int)
    )

    data = {
        'cards': cards
    }

    return create_response(data=data)
