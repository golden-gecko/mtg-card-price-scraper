import hashlib
import json
import os
import requests
import shutil
import time
import uuid

from datetime import datetime
from requests.exceptions import ConnectionError
from urllib3.exceptions import MaxRetryError

from log import get_logger


logger = get_logger()


class ExpirationTime:
    minute = 60
    hour = 60 * 60
    day = 60 * 60 * 24
    week = 60 * 60 * 24 * 7
    month = 60 * 60 * 24 * 30


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


def download(url: str, proxy: str = None) -> tuple:
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
        response = requests.get(url, proxies=proxies, timeout=10)
        download_time = get_duration(start)
    except Exception as e:
        logger.error('Failed to download: %s', e)
        return None, None, None, str(e)

    logger.debug('Response status_code: %d', response.status_code)

    if response.status_code != 200:
        return None, response.status_code, None, None

    return response.text, response.status_code, download_time, None


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


def get_hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def get_uuid() -> str:
    return str(uuid.uuid4())


def get_timestamp() -> str:
    date = datetime.utcnow()

    if date.microsecond == 0:
        date_str = '{}.000000'.format(date.isoformat())
    else:
        date_str = date.isoformat()

    return date_str


def load_file(file_name: str) -> str:
    logger.debug('Loading file "%s"', file_name)

    with open(file_name, 'rb') as file:
        return file.read().decode('utf-8')


def save_to_file(file_name: str, data: str):
    logger.debug('Saving file "%s"', file_name)

    directory_name = os.path.dirname(file_name)

    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    with open(file_name, 'wb') as file:
        file.write(data.encode('utf-8'))


def get_time() -> datetime:
    return datetime.utcnow()


def get_duration(start: datetime) -> float:
    return (get_time() - start).total_seconds()


def wait(seconds: float):
    time.sleep(seconds)


def get_queue_name(name: str, type: str) -> str:
    return 'scraper_{}_{}'.format(name, type)


def get_default_expiration_time() -> int:
    return ExpirationTime.month


def sort_keys(value: dict) -> dict:
    return json.loads(json.dumps(value, sort_keys=True))


class ExecutionTime:
    def __init__(self, name: str):
        self.name = name
        self.start = None

    def __enter__(self):
        self.start = get_time()

    def __exit__(self, type, value, traceback):
        logger.debug('%s took %s seconds', self.name, get_duration(self.start))
