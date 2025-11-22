from helpers import create_response
from mongo import MongoGatherer
from rabbit import RabbitClient
from scrapers.gatherer import GathererClient


def route_cards(card_id):
    mongo = MongoGatherer(host='mongo')

    rabbit = RabbitClient(host='rabbit')
    rabbit.connect()

    gatherer = GathererClient(mongo=mongo, rabbit=rabbit)

    if gatherer.queue_card(card_id=card_id):
        code = 200
    else:
        code = 500

    return create_response(code=code)


def route_pages(page_id):
    mongo = MongoGatherer(host='mongo')

    rabbit = RabbitClient(host='rabbit')
    rabbit.connect()

    gatherer = GathererClient(mongo=mongo, rabbit=rabbit)

    if gatherer.queue_page(page_id=page_id):
        code = 200
    else:
        code = 500

    return create_response(code=code)
