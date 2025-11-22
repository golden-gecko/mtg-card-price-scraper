import connexion
import os

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from http import HTTPStatus

from config import Config
from helpers import create_response
from models import db


def route_error(error):
    return create_response(code=error.code, message=str(error.description))


connexion_app = connexion.App(__name__, specification_dir=os.path.abspath(os.path.dirname(__file__)))
connexion_app.add_api('api_v1.yaml', validate_responses=True)

app = connexion_app.app
app.config.from_object(Config)

codes = [
    HTTPStatus.BAD_REQUEST,
    HTTPStatus.UNAUTHORIZED,
    HTTPStatus.FORBIDDEN,
    HTTPStatus.NOT_FOUND,
    HTTPStatus.METHOD_NOT_ALLOWED,
    HTTPStatus.UNPROCESSABLE_ENTITY,
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.SERVICE_UNAVAILABLE
]

for code in codes:
    app.register_error_handler(code, route_error)

db.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)


@jwt.expired_token_loader
def expired_token_loader_callback(token):
    return create_response(
        code=HTTPStatus.UNAUTHORIZED,
        message='Token has expired'
    )


@jwt.invalid_token_loader
def expired_token_loader_callback(token):
    return create_response(
        code=HTTPStatus.UNPROCESSABLE_ENTITY,
        message='Token is invalid'
    )


@jwt.revoked_token_loader
def expired_token_loader_callback(token):
    return create_response(
        code=HTTPStatus.UNAUTHORIZED,
        message='Token has been revoked'
    )


CORS(app, resources={'/*': {'origins': '*'}})


from models import Deck, User
