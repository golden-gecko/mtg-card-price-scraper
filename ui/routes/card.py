from flask import abort, render_template
from http import HTTPStatus

import config

from app import app
from helpers import make_url, send_get
from log import get_logger


logger = get_logger()


@app.route('/card/<int:card_id>')
def route_card(card_id: int):
    response = send_get(make_url(config.API_URL, ['mtg', 'cards', card_id]))

    if response.status_code != HTTPStatus.OK:
        abort(HTTPStatus.NOT_FOUND)

    variables = {
        'active_page': 'search',
        'card': response.json()['data']['card']
    }

    logger.debug('variables: %s', variables)

    return render_template('card.html', **variables)
