import datetime
import logging
import os


API_HOST = os.environ.get('API_HOST')
API_PORT = int(os.environ.get('API_PORT'))
API_URL = 'http://{host}:{port}/v1/'.format(host=API_HOST, port=API_PORT)

ELASTIC_HOST = os.environ.get('ELASTIC_HOST')
ELASTIC_PORT = int(os.environ.get('ELASTIC_PORT'))

LOG_LEVEL = logging.DEBUG

MINIO_HOST = os.environ.get('MINIO_HOST')
MINIO_PORT = int(os.environ.get('MINIO_PORT'))

MONGO_HOST = os.environ.get('MONGO_HOST')
MONGO_PORT = int(os.environ.get('MONGO_PORT'))

POSTGRES_DRIVER = 'postgresql+psycopg2'
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_DATABASE_NAME = 'cenykart'
POSTGRES_PASSWORD = 'ca978112ca1bbdcafac2'
POSTGRES_PORT = int(os.environ.get('POSTGRES_PORT'))
POSTGRES_USER = 'cenykart'

RABBIT_HOST = os.environ.get('RABBIT_HOST')
RABBIT_PORT = int(os.environ.get('RABBIT_PORT'))

STATIC_HOST = os.environ.get('STATIC_HOST')
STATIC_PORT = int(os.environ.get('STATIC_PORT'))
STATIC_URL = 'http://{host}:{port}/'.format(host=STATIC_HOST, port=STATIC_PORT)


class AppConfig:
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)
    JWT_SECRET_KEY = '3e23e8160039594a3389'

    SECRET_KEY = '3e23e8160039594a3389'

    SQLALCHEMY_DATABASE_URI = '{driver}://{user}:{password}@{host}:{port}/{name}'.format(
        driver=POSTGRES_DRIVER,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        name=POSTGRES_DATABASE_NAME
    )
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
