import connexion
import os

from flask import jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config
from helpers import create_error_response


connexion_app = connexion.App(__name__, specification_dir=os.path.abspath(os.path.dirname(__file__)))

app = connexion_app.app
app.config.from_object(Config)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

connexion_app.add_api('api_v1.yaml')


@app.errorhandler(400)
def not_found_error(error):
    return jsonify(create_error_response(code=404, message=str(error))), 400


@app.errorhandler(401)
def not_found_error(error):
    return jsonify(create_error_response(code=404, message=str(error))), 401


@app.errorhandler(403)
def not_found_error(error):
    return jsonify(create_error_response(code=404, message=str(error))), 403


@app.errorhandler(404)
def not_found_error(error):
    return jsonify(create_error_response(code=404, message=str(error))), 404


@app.errorhandler(422)
def not_found_error(error):
    return jsonify(create_error_response(code=404, message=str(error))), 422


@app.errorhandler(500)
def internal_error(error):
    return jsonify(create_error_response(code=500, message=str(error))), 500
