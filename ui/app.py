import http
import jwt

from flask import Flask
from flask_login import LoginManager

from config import Config
from helpers import create_response
from log import get_logger


def route_error(error):
    return create_response(code=error.code, message=str(error.description))


logger = get_logger()

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

login_manager = LoginManager()
login_manager.init_app(app)


class User:
    def __init__(self, token):
        self.token = token

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return ''

    def get_token(self):
        return self.token

    def __repr__(self):
        return '<User is_authenticated={}, is_active={}, is_anonymous={}, id={}, token={}>'.format(
            self.is_authenticated(), self.is_active(), self.is_anonymous(), self.get_id(), self.get_token()
        )

@login_manager.user_loader
def load_user(token):
    return User(token)


from routes import account, auth, index, register, search
