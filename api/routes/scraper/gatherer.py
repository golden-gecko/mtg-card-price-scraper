from flask import jsonify
from redis import Redis

from helpers import create_error_response
from gatherer import GathererClient
from mongo import Mongo
from rabbit import RabbitClient


def route_cards(id):
    mongo = Mongo('mongo')
    rabbit = RabbitClient(host='rabbit')
    redis = Redis(host='redis')

    gatherer = GathererClient(mongo=mongo, rabbit=rabbit, redis=redis)

    if gatherer.queue_card(card_id=id):
        code = 200
    else:
        code = 500

    return jsonify(create_error_response(code=code)), code


def route_pages(id):
    mongo = Mongo('mongo')
    rabbit = RabbitClient(host='rabbit')
    redis = Redis(host='redis')

    gatherer = GathererClient(mongo=mongo, rabbit=rabbit, redis=redis)

    if gatherer.queue_page(page_id=id):
        code = 200
    else:
        code = 500

    return jsonify(create_error_response(code=code)), code
