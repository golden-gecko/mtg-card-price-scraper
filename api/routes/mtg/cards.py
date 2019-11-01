from flask import request

from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_get_cards():
    db = GathererDb(host='mongo')

    params = {
        'all_versions': request.args.get('all_versions', default=False, type=bool),
        'block': request.args.get('block'),
        'color': request.args.get('color'),
        'expansion': request.args.get('expansion'),
        'format': request.args.get('format'),
        'name': request.args.get('name'),
        'rarity': request.args.get('rarity'),
        'type': request.args.get('type'),
        'subtype': request.args.get('subtype')
    }

    cards = db.get_cards(
        params=params,
        page=request.args.get('page', default=0, type=int),
        limit=request.args.get('limit', default=12, type=int)
    )

    data = {
        'cards': cards
    }

    return create_response(data=data)


def route_get_card_details(card_id: int):
    db = GathererDb(host='mongo')

    card = db.get_card(
        card_id=card_id
    )

    data = {
        'card': card
    }

    return create_response(data=data)
