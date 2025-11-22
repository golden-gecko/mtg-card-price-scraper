from flask import jsonify

from models.type import Type


def route_types():
    types = Type.query.all()

    response = {
        'data': {
            'types': types
        },
        'status': {
            'code': 200
        }
    }

    return jsonify(response)
