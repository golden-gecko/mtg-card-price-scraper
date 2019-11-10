from flask import Blueprint, render_template, request
from http import HTTPStatus

import config

from helpers import make_url, send_get
from log import get_logger


blueprint = Blueprint('search', __name__)
logger = get_logger()


def get_items(name, params=None):
    response = send_get(make_url(config.API_URL, ['mtg', name]), params=params)

    if response.status_code != HTTPStatus.OK:
        return None

    response = response.json()

    if 'data' not in response:
        return None

    response = response['data']

    if name not in response:
        return None

    return response[name]


@blueprint.route('/search')
def route_search():
    params = {
        'artist': request.args.get('artist', default=''),
        'block': request.args.get('block', default=''),
        'color': request.args.get('color', default=''),
        'format': request.args.get('format', default=''),
        'limit': request.args.get('limit', default=12, type=int),
        'name': request.args.get('name', default=''),
        'number': request.args.get('number', default=''),
        'power': request.args.get('power', default=''),
        'rarity': request.args.get('rarity', default=''),
        'set': request.args.get('set', default=''),
        'subtype': request.args.get('subtype', default=''),
        'toughness': request.args.get('toughness', default=''),
        'type': request.args.get('type', default=''),
        'watermark': request.args.get('watermark', default='')
    }

    logger.debug('params: %s', params)

    variables = {
        'cards': get_items('cards', params=params),
        'search_options': {
            'artists': get_items('artists'),
            'blocks': get_items('blocks'),
            'colors': get_items('colors'),
            'formats': get_items('formats'),
            'limits': [{'name': x} for x in range(12, 97, 12)],
            'rarities': get_items('rarities'),
            'sets': get_items('sets'),
            'subtypes': get_items('subtypes'),
            'types': get_items('types'),
            'watermarks': get_items('watermarks')
        },
        'search_params': params
    }

    return render_template('search.html', active_page='search', **variables)
