import http
import requests

from requests import Response

from flask import jsonify
from log import get_logger


def create_response(code: int = http.HTTPStatus.OK, message: str = '', data=None) -> tuple:
    response = {
        'code': code
    }

    if message:
        response['message'] = message

    if data:
        response['data'] = data

    return jsonify(response), code


def send_get(url: str, params=None) -> Response:
    logger = get_logger()

    logger.debug('Sending GET to %s...', url)

    response = requests.get(url=url, params=params)

    logger.debug('Received %d %s', response.status_code, response.text)

    return response


def send_post(url: str, json=None, params=None) -> Response:
    logger = get_logger()

    logger.debug('Sending POST to %s...', url)

    response = requests.post(url=url, json=json, params=params)

    logger.debug('Received %d %s', response.status_code, response.text)

    return response
