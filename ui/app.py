import jwt

from flask import Flask, render_template, request
from flask_login import LoginManager, UserMixin
from http import HTTPStatus

import config

from helpers import make_url, send_get
from log import get_logger


def route_error(error):
    return render_template('errors/{}.html'.format(error.code)), error.code


logger = get_logger()

app = Flask(__name__)
app.config.from_object(config.Config)

codes = [
    HTTPStatus.BAD_REQUEST,
    HTTPStatus.NOT_FOUND,
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.SERVICE_UNAVAILABLE
]

for code in codes:
    app.register_error_handler(code, route_error)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'


class User(UserMixin):
    def __init__(self, id=None, token=None, data=None):
        logger.debug('User.__init__(): %s, %s, %s', id, token, data)

        self.id = id
        self.token = token
        self.data = data

        if not self.id and self.token:
            try:
                decoded = jwt.decode(self.token, app.config.get('SECRET_KEY'))
            except jwt.ExpiredSignatureError as e:
                logger.warning('Failed to decode token "%s": %s', self.token, e)
                logger.debug('User.is_authenticated(): False (1)')
            except jwt.InvalidTokenError as e:
                logger.warning('Failed to decode token "%s": %s', self.token, e)
                logger.debug('User.is_authenticated(): False (2)')
            else:
                self.id = decoded['identity']

    @property
    def is_authenticated(self):
        logger.debug('User.is_authenticated()')

        return True

    @property
    def is_active(self):
        logger.debug('User.is_active(): %s, %s, %s', self.id, self.token, self.data)

        return self.is_authenticated

    @property
    def is_anonymous(self):
        logger.debug('User.is_anonymous(): %s, %s, %s', self.id, self.token, self.data)

        return self.is_authenticated is False or self.is_active is False

    def get_id(self):
        logger.debug('User.get_id(): %s, %s, %s', self.id, self.token, self.data)

        return self.id

    def get_token(self):
        logger.debug('User.get_token(): %s, %s, %s', self.id, self.token, self.data)

        return self.token

    def get_data(self):
        logger.debug('User.get_token(): %s, %s, %s', self.id, self.token, self.data)

        return self.data

    def __repr__(self):
        return '<User is_authenticated={}, is_active={}, is_anonymous={}, id={}, token={}, data={}>'.format(
            self.is_authenticated, self.is_active, self.is_anonymous, self.get_id(), self.get_token(), self.get_data()
        )


@login_manager.user_loader
def load_user(id):
    logger.debug('load_user(): %s', id)

    token = request.cookies.get('jwt')

    headers = {
        'Authorization': 'Bearer {}'.format(token)
    }

    response = send_get(make_url(config.API_URL, ['users', id]), headers=headers)

    if response.status_code != HTTPStatus.OK:
        return None

    return User(id=id, token=token, data=response.json()['data'])


from routes import auth, card, index, profile, register, search
