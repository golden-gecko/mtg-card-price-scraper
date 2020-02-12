from flask import Flask, render_template, request
from flask_login import LoginManager
from http import HTTPStatus

import config

from helpers import make_url, send_get
from log import get_logger
from routes.auth import blueprint as auth_blueprint
from routes.card import blueprint as card_blueprint
from routes.contact import blueprint as contact_blueprint
from routes.index import blueprint as index_blueprint
from routes.parser import blueprint as parser_blueprint
from routes.profile import blueprint as profile_blueprint
from routes.register import blueprint as register_blueprint
from routes.search import blueprint as search_blueprint


def route_error(error):
    return render_template('errors/{}.html'.format(error.code)), error.code


logger = get_logger()

app = Flask(__name__)
app.config.from_object(config.AppConfig)
app.register_blueprint(auth_blueprint)
app.register_blueprint(card_blueprint)
app.register_blueprint(contact_blueprint)
app.register_blueprint(index_blueprint)
app.register_blueprint(parser_blueprint)
app.register_blueprint(profile_blueprint)
app.register_blueprint(register_blueprint)
app.register_blueprint(search_blueprint)

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

    # TODO: Fix circular dependency.
    from app_user import User

    return User(id=id, token=token, data=response.json()['data'])
