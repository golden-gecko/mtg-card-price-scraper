import http

from helpers import create_response
from scrapers.gatherer.client import GathererClient
from scrapers.gatherer.db import GathererDb
from scrapers.gatherer.queue import GathererQueue


def route_cards(card_id):
    db = GathererDb(host='mongo')

    queue = GathererQueue(host='rabbit')
    queue.connect()

    gatherer = GathererClient(db=db, queue=queue)

    if gatherer.queue_card(card_id=card_id):
        code = http.HTTPStatus.OK
    else:
        code = http.HTTPStatus.INTERNAL_SERVER_ERROR

    return create_response(code=code)


def route_pages(page_id):
    db = GathererDb(host='mongo')

    queue = GathererQueue(host='rabbit')
    queue.connect()

    gatherer = GathererClient(db=db, queue=queue)

    if gatherer.queue_page(page_id=page_id):
        code = http.HTTPStatus.OK
    else:
        code = http.HTTPStatus.INTERNAL_SERVER_ERROR

    return create_response(code=code)
