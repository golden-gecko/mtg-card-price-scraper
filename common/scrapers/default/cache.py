import datetime
import os
import re
import shutil

from log import get_logger
from utils import get_hash, get_timestamp, get_uuid, load_file, save_to_file


class ScraperCache:
    def __init__(self, directory: str):
        self.logger = get_logger()

        self.directory = directory

    def get(self, prefix: str, name: str, expiration_time: int):
        self.logger.debug('ScraperCache.get(%s, %s, %s)', prefix, name, expiration_time)

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

            if total_seconds > expiration_time:
                return None, None, None

            return load_file(path), path, path_time.isoformat()

        return None, None, None

    def get_path(self, prefix: str, name: str) -> str:
        return os.path.join(self.directory, prefix, get_hash(name))

    def set(self, prefix: str, name: str, value: str):
        path = self.get_path(prefix, name)

        timestamp = get_timestamp()
        timestamp_escaped = re.sub('[^0-9]+', '_', timestamp)

        path_tmp = os.path.join(path, get_uuid())
        path = os.path.join(path, timestamp_escaped)

        save_to_file(path_tmp, value)

        self.logger.debug('Moving file "%s"', path)

        shutil.move(path_tmp, path)

        return path, timestamp
