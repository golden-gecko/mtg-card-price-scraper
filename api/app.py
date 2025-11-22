import connexion
import os

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config
from helpers import create_response


def route_error(error):
    return create_response(code=error.code, message=str(error.description))


connexion_app = connexion.App(__name__, specification_dir=os.path.abspath(os.path.dirname(__file__)))

app = connexion_app.app
app.config.from_object(Config)

for code in [400, 401, 403, 404, 405, 422, 500]:
    app.register_error_handler(code, route_error)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

connexion_app.add_api('api_v1.yaml')
