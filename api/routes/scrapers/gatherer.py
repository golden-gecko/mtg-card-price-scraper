from helpers import create_response
from gatherer import GathererClient
from mongo import Mongo
from rabbit import RabbitClient


def route_cards(card_id):
    mongo = Mongo(host='mongo')
    rabbit = RabbitClient(host='rabbit')

    gatherer = GathererClient(mongo=mongo, rabbit=rabbit)

    if gatherer.queue_card(card_id=card_id):
        code = 200
    else:
        code = 500

    return create_response(code=code)


def route_pages(page_id):
    mongo = Mongo(host='mongo')
    rabbit = RabbitClient(host='rabbit')

    gatherer = GathererClient(mongo=mongo, rabbit=rabbit)

    if gatherer.queue_page(page_id=page_id):
        code = 200
    else:
        code = 500

    return create_response(code=code)
