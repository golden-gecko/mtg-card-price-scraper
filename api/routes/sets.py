from flask import jsonify

from models.set import Set


def route_sets():
    sets = Set.query.all()

    response = {
        'data': {
            'sets': sets
        },
        'status': {
            'code': 200
        }
    }

    return jsonify(response)
