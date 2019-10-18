import os
import requests
import shutil
import uuid

from requests.exceptions import ConnectionError
from urllib3.exceptions import MaxRetryError

from datetime import datetime
from log import get_logger


logger = get_logger(__name__)


def download_and_save_image(url: str, file_name: str):
    logger.debug('Trying to download %s', url)

    try:
        response = requests.get(url, stream=True)
    except (ConnectionError, MaxRetryError) as e:
        logger.error('Failed to download: %s', e)
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


def download(url: str, proxy=None):
    logger.debug('Trying to download %s', url)

    if proxy:
        proxies = {
            'http': proxy,
            'https': proxy
        }
    else:
        proxies = None

    try:
        start = get_time()
        response = requests.get(url, proxies=proxies)
        download_time = get_duration(start)
    except (ConnectionError, MaxRetryError) as e:
        logger.error('Failed to download: %s', e)
        return False, None

    logger.debug('Response status_code: %d', response.status_code)

    if response.status_code != 200:
        return False, None

    return response.text, download_time


def download_and_save_text(url: str, file_name: str):
    logger.debug('Trying to download %s', url)

    try:
        response = requests.get(url)
    except (ConnectionError, MaxRetryError) as e:
        logger.error('Failed to download: %s', e)
        return False

    logger.debug('Response status_code: %d', response.status_code)

    if response.status_code != 200:
        return False

    save_to_file(file_name, response.text)

    return response.text


def get_uuid() -> str:
    return str(uuid.uuid4())


def get_timestamp() -> str:
    return datetime.utcnow().isoformat()


def load_file(file_name) -> str:
    logger.debug('Loading file "%s"', file_name)

    with open(file_name, 'rb') as file:
        return file.read().decode('utf-8')


def save_to_file(file_name: str, data) -> None:
    logger.debug('Saving file "%s"', file_name)

    directory_name = os.path.dirname(file_name)

    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    with open(file_name, 'wb') as file:
        file.write(data.encode('utf-8'))


def get_time():
    return datetime.utcnow()


def get_duration(start):
    return (get_time() - start).total_seconds()


class ExecutionTime:
    def __init__(self, name: str):
        self.name = name
        self.start = None

    def __enter__(self):
        self.start = get_time()

    def __exit__(self, type, value, traceback):
        logger.debug('%s took %s seconds', self.name, get_duration(self.start))
