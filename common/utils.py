import os
import requests
import shutil
import uuid

from requests.exceptions import ConnectionError
from urllib3.exceptions import MaxRetryError

from datetime import datetime
from log import get_logger


def download_and_save_image(url, file_name):
    logger = get_logger(__name__)

    try:
        response = requests.get(url, stream=True)
    except (ConnectionError, MaxRetryError) as e:
        logger.error('Failed to download "%s": %s', url, e)
        return False

    if response.status_code != 200:
        logger.error('Request failed: %d', response.status_code)
        return False

    directory_name = os.path.dirname(file_name)

    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    with open(file_name, 'wb') as file:
        response.raw.decode_content = True

        shutil.copyfileobj(response.raw, file)

    return response.raw


def download_and_save_text(url, file_name):
    logger = get_logger(__name__)
    logger.debug('Trying to download %s and save to %s', url, file_name)

    try:
        response = requests.get(url)
    except (ConnectionError, MaxRetryError) as e:
        logger.error('Failed to download "%s": %s', url, e)
        return False

    logger.debug('Response status_code: %d', response.status_code)

    if response.status_code != 200:
        return False

    save_to_file(file_name, response.text)

    return response.text


def get_uuid():
    return str(uuid.uuid4())


def get_timestamp():
    return '{}Z'.format(datetime.utcnow().isoformat())


def load_file(file_name):
    with open(file_name, 'rb') as file:
        return file.read().decode('utf-8')


def save_to_file(file_name, data):
    directory_name = os.path.dirname(file_name)

    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    with open(file_name, 'wb') as file:
        file.write(data.encode('utf-8'))
