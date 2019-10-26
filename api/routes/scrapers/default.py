import json
import http

from flask import request

from helpers import create_response
from log import get_logger
from scrapers.default.db import ScraperDb
from scrapers.default.queue import ScraperQueue


logger = get_logger()


def route_pages_post():
    queue = ScraperQueue('rabbit')
    queue.connect()

    page = request.json

    logger.debug(page)

    if page.keys() != {'configuration', 'stage', 'url'}:
        return create_response(code=http.HTTPStatus.BAD_REQUEST)

    queue.publish('scraper_{}'.format(page['configuration']), json.dumps(page))

    return create_response()


def route_pages_put():
    queue = ScraperQueue('rabbit')
    queue.connect()

    page = request.json

    logger.debug(page)

    if page.keys() != {'configuration', 'stage', 'url'}:
        return create_response(code=http.HTTPStatus.BAD_REQUEST)

    page['refresh'] = True

    queue.publish('scraper_{}'.format(page['configuration']), json.dumps(page))

    return create_response()


def route_statistics():
    db = ScraperDb('mongo', 'scraper')

    statistics = {
        'db': db.get_statistics()
    }

    return create_response(data=statistics)
