import http

from flask import Flask

from config import Config
from helpers import create_response


def route_error(error):
    return create_response(code=error.code, message=str(error.description))


app = Flask(__name__)
app.config.from_object(Config)

codes = [
    http.HTTPStatus.BAD_REQUEST,
    http.HTTPStatus.UNAUTHORIZED,
    http.HTTPStatus.FORBIDDEN,
    http.HTTPStatus.NOT_FOUND,
    http.HTTPStatus.METHOD_NOT_ALLOWED,
    http.HTTPStatus.UNPROCESSABLE_ENTITY,
    http.HTTPStatus.INTERNAL_SERVER_ERROR,
    http.HTTPStatus.SERVICE_UNAVAILABLE
]

for code in codes:
    app.register_error_handler(code, route_error)


from routes import account, auth, index, register, search
