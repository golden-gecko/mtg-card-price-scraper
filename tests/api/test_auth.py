import config

from http import HTTPStatus

from common.helpers import make_url, send_delete


def test_logout_without_token():
    response = send_delete(make_url(config.API_URL, ['auth']))

    assert response.status_code == HTTPStatus.UNAUTHORIZED
