from pymongo import ASCENDING, MongoClient
from pymongo.results import InsertOneResult

import config

from log import get_logger


class ScraperDb:
    def __init__(self, host: str = config.MONGO_HOST, port: int = config.MONGO_PORT, database: str = None):
        self.logger = get_logger()

        self.client = MongoClient(host=host, port=port)

        self.db = self.client[database]
        self.db.pages.create_index([('configuration', ASCENDING), ('stage', ASCENDING), ('url', ASCENDING)], unique=True)
        self.db.pages_2.create_index([('cache_path', ASCENDING)], unique=True)

    def get_statistics(self):
        cursor = self.db.pages.aggregate([
            {
                '$group': {
                    '_id': {
                        'configuration': '$configuration',
                        'stage': '$stage'
                    },
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ])

        statistics = {}

        for item in cursor:
            if item['_id']['configuration'] not in statistics:
                statistics[item['_id']['configuration']] = {}

            statistics[item['_id']['configuration']][item['_id']['stage']] = item['count']

        return statistics

    def has_page(self, configuration: str, stage: str, url: str):
        return self.db.pages.find_one({
            'configuration': configuration,
            'stage': stage,
            'url': url
        })

    def has_version(self, cache_path: str):
        return self.db.pages.find_one({
            'versions.cache.path': cache_path
        })

    def index_page(self, data: dict) -> InsertOneResult:
        return self.db.pages_2.insert_one(data)

    def index_stats(self, data: dict) -> InsertOneResult:
        return self.db.stats.insert_one(data)
