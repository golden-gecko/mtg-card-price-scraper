from flask import Blueprint, render_template, request
from http import HTTPStatus

import config

from helpers import make_url, send_get


blueprint = Blueprint('search', __name__)


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
        'expansion': request.args.get('expansion', default=''),
        'format': request.args.get('format', default=''),
        'name': request.args.get('name', default=''),
        'number': request.args.get('number', default=''),
        'rarity': request.args.get('rarity', default=''),
        'subtype': request.args.get('subtype', default=''),
        'type': request.args.get('type', default=''),
        'watermark': request.args.get('watermark', default='')
    }

    variables = {
        'artists': get_items('artists'),
        'blocks': get_items('blocks'),
        'cards': get_items('cards', params=params),
        'colors': get_items('colors'),
        'expansions': get_items('expansions'),
        'formats': get_items('formats'),
        'rarities': get_items('rarities'),
        'subtypes': get_items('subtypes'),
        'types': get_items('types'),
        'watermarks': get_items('watermarks')
    }

    return render_template('search.html', active_page='search', **variables)
