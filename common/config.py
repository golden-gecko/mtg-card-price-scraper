import datetime
import logging


API_HOST = '10.10.0.10'
API_PORT = 8000
API_URL = 'http://{host}:{port}/v1/'.format(host=API_HOST, port=API_PORT)

DATABASE_DRIVER = 'postgresql+psycopg2'
DATABASE_HOST = '10.10.0.15'
DATABASE_NAME = 'cenykart'
DATABASE_PASSWORD = 'ca978112ca1bbdcafac2'
DATABASE_PORT = 5432
DATABASE_USER = 'cenykart'

LOG_LEVEL = logging.DEBUG

MONGO_HOST = '10.10.0.13'
MONGO_PORT = 27017

RABBIT_HOST = '10.10.0.16'
RABBIT_PORT = 5672

STATIC_HOST = '10.10.0.18'
STATIC_PORT = 8080
STATIC_URL = 'http://{host}:{port}/'.format(host=STATIC_HOST, port=STATIC_PORT)


class AppConfig:
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)
    JWT_SECRET_KEY = '3e23e8160039594a3389'

    SECRET_KEY = '3e23e8160039594a3389'

    SQLALCHEMY_DATABASE_URI = '{driver}://{user}:{password}@{host}:{port}/{name}'.format(
        driver=DATABASE_DRIVER,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        name=DATABASE_NAME
    )
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
