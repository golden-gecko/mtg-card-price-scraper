from flask import request

from helpers import create_response
from scrapers.gatherer.db import GathererDb


def route_get_cards():
    db = GathererDb(host='mongo')

    params = {
        'all_versions': request.args.get('all_versions', default=False, type=bool),
        'artist': request.args.get('artist'),
        'block': request.args.get('block'),
        'color': request.args.get('color'),
        'format': request.args.get('format'),
        'name': request.args.get('name'),
        'number': request.args.get('number'),
        'power': request.args.get('power'),
        'rarity': request.args.get('rarity'),
        'set': request.args.get('set'),
        'subtype': request.args.get('subtype'),
        'toughness': request.args.get('toughness'),
        'type': request.args.get('type'),
        'watermark': request.args.get('watermark')
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
