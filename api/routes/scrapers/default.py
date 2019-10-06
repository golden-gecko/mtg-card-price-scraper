import json

from flask import request

from helpers import create_response
from log import get_logger
from scrapers.default.db import ScraperDb
from scrapers.default.queue import ScraperQueue


def route_pages_post():
    queue = ScraperQueue('rabbit')
    queue.connect()

    page = request.json

    get_logger().debug(page)

    if page.keys() != {'configuration', 'stage', 'url'}:
        return create_response(code=400)

    queue.publish('scraper_{}'.format(page['configuration']), json.dumps(page))

    return create_response(code=200)


def route_pages_put():
    queue = ScraperQueue('rabbit')
    queue.connect()

    page = request.json

    get_logger().debug(page)

    if page.keys() != {'configuration', 'stage', 'url'}:
        return create_response(code=400)

    page['refresh'] = True

    queue.publish('scraper_{}'.format(page['configuration']), json.dumps(page))

    return create_response(code=200)


def route_statistics():
    db = ScraperDb('mongo', 'scraper')

    statistics = {
        'db': db.get_statistics()
    }

    return create_response(code=200, data=statistics)
