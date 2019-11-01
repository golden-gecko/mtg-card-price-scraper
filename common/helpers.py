import requests

from http import HTTPStatus
from requests import Response

from flask import jsonify
from log import get_logger


def create_response(code: int = HTTPStatus.OK, message: str = '', data=None) -> tuple:
    response = {
        'code': code
    }

    if message:
        response['message'] = message

    if data:
        response['data'] = data

    return jsonify(response), code


def send_get(url: str, headers=None, params=None) -> Response:
    logger = get_logger()

    logger.debug('Sending GET to %s...', url)

    response = requests.get(url=url, headers=headers, params=params)

    logger.debug('Received %d %s', response.status_code, response.text)

    return response


def send_post(url: str, headers=None, json=None, params=None) -> Response:
    logger = get_logger()

    logger.debug('Sending POST to %s...', url)

    if json:
        if not headers:
            headers = {}

        headers['Content-Type'] = 'application/json'

    response = requests.post(url=url, headers=headers, json=json, params=params)

    logger.debug('Received %d %s', response.status_code, response.text)

    return response
