import requests

from flask import jsonify
from log import get_logger


def create_response(code: int, message=None, data=None):
    response = {
        'code': code
    }

    if message:
        response['message'] = message

    if data:
        response['data'] = data

    return jsonify(response), code


def send_get(url):
    logger = get_logger(__name__)

    logger.debug('Sending GET to %s...', url)

    response = requests.get(url=url)

    logger.debug('Received %d %s', response.status_code, response.text)

    return response
