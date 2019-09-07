from flask import jsonify


def create_response(code: int, message=None, data=None):
    response = {
        'code': code
    }

    if message:
        response['message'] = message

    if data:
        response['data'] = data

    return jsonify(response), code
