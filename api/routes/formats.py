from flask import jsonify

from models.format import Format


def route_formats():
    formats = Format.query.all()

    response = {
        'data': {
            'formats': formats
        },
        'status': {
            'code': 200
        }
    }

    return jsonify(response)
