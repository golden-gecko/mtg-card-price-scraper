import connexion
import http
import os

from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config
from helpers import create_response


def route_error(error):
    return create_response(code=error.code, message=str(error.description))


connexion_app = connexion.App(__name__, specification_dir=os.path.abspath(os.path.dirname(__file__)))

app = connexion_app.app
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

db = SQLAlchemy(app)

migrate = Migrate(app, db)

connexion_app.add_api('api_v1.yaml')

CORS(app, resources={
    '/*': {
        'origins': '*'
    }
})
