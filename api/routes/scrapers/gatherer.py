from flask import request

from helpers import create_response
from scrapers.gatherer.client import GathererClient
from scrapers.gatherer.db import GathererDb
from scrapers.gatherer.queue import GathererQueue


def route_cards(card_id: int):
    db = GathererDb()

    queue = GathererQueue()
    queue.connect()

    gatherer = GathererClient(db=db, queue=queue)
    gatherer.queue_card(card_id=card_id, refresh=request.args.get('refresh', default=False, type=bool))

    return create_response()


def route_pages(page_id: int):
    db = GathererDb()

    queue = GathererQueue()
    queue.connect()

    gatherer = GathererClient(db=db, queue=queue)
    gatherer.queue_page(page_id=page_id, refresh=request.args.get('refresh', default=False, type=bool))

    return create_response()
