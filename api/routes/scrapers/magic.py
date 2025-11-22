from helpers import create_response
from magic import MagicClient
from mongo import MongoMagic
from rabbit import RabbitClient


def route_cards(card_id):
    mongo = MongoMagic(host='mongo')

    rabbit = RabbitClient(host='rabbit')
    rabbit.connect()

    magic = MagicClient(mongo=mongo, rabbit=rabbit)

    if magic.queue_card(card_id=card_id):
        code = 200
    else:
        code = 500

    return create_response(code=code)


def route_pages(page_id):
    mongo = MongoMagic(host='mongo')

    rabbit = RabbitClient(host='rabbit')
    rabbit.connect()

    magic = MagicClient(mongo=mongo, rabbit=rabbit)

    if magic.queue_page(page_id=page_id):
        code = 200
    else:
        code = 500

    return create_response(code=code)
