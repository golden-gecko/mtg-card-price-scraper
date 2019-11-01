from flask import render_template, request
from http import HTTPStatus
from urllib.parse import urljoin

import config

from app import app
from helpers import send_get


def get_items(name, params=None):
    response = send_get(urljoin(config.API_URL, '/'.join(['mtg', name])), params=params)

    if response.status_code != HTTPStatus.OK:
        return None

    response = response.json()

    if 'data' not in response:
        return None

    response = response['data']

    if name not in response:
        return None

    return response[name]


@app.route('/search')
def route_search():
    params = {
        'name': request.args.get('name', default='')
    }

    variables = {
        'blocks': get_items('blocks'),
        'cards': get_items('cards', params=params),
        'colors': get_items('colors'),
        'expansions': get_items('expansions'),
        'formats': get_items('formats'),
        'rarities': get_items('rarities'),
        'subtypes': get_items('subtypes'),
        'types': get_items('types')
    }

    return render_template('search.html', active_page='search', **variables)
