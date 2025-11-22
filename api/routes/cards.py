from flask import jsonify

from models.card import Card


def route_cards():
    cards = Card.query.all()

    response = {
        'data': {
            'cards': cards
        },
        'status': {
            'code': 200
        }
    }

    return jsonify(response)
