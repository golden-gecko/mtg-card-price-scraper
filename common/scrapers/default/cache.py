import datetime
import hashlib
import os
import re

import config

from log import get_logger
from utils import get_timestamp, load_file, save_to_file


class ScraperCache:
    def __init__(self, directory):
        self.logger = get_logger()

        self.directory = directory

    def get(self, prefix, name):
        path = self.get_path(prefix, name)

        if not os.path.exists(path):
            return None, None, None

        for root, _, files in os.walk(path):
            if not len(files):
                return None, None, None

            files = sorted(files, reverse=True)

            path = os.path.join(root, files[0])
            path_time = datetime.datetime.strptime(files[0], '%Y_%m_%d_%H_%M_%S_%f')

            total_seconds = (datetime.datetime.utcnow() - path_time).total_seconds()

            self.logger.warning('Cache is %d seconds old', total_seconds)

            if total_seconds > config.SCRAPER_CACHE_EXPIRATION_TIME:
                return None, None, None

            return load_file(path), path, path_time.isoformat()

        return None, None, None

    def get_hash(self, name):
        return hashlib.sha256(name.encode()).hexdigest()

    def get_path(self, prefix, name):
        return os.path.join(self.directory, prefix, self.get_hash(name))

    def set(self, prefix, name, value):
        path = self.get_path(prefix, name)
        timestamp = get_timestamp()
        timestamp_escaped = re.sub('[^0-9]+', '_', timestamp)
        path = os.path.join(path, timestamp_escaped)

        save_to_file(path, value)

        return path, timestamp
