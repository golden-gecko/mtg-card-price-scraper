from pymongo import ASCENDING, MongoClient

from log import get_logger


class ScraperDb:
    def __init__(self, host, database):
        self.client = MongoClient(host)

        self.db = self.client[database]
        self.db.pages.create_index([('configuration', ASCENDING), ('stage', ASCENDING), ('url', ASCENDING)], unique=True)

        self.logger = get_logger(__name__)

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

    def has_page(self, configuration, stage, url):
        return self.db.pages.find_one({
            'configuration': configuration,
            'stage': stage,
            'url': url
        })

    def index_page(self, data):
        return self.db.pages.insert_one(data)

    def index_version(self, query, data):
        # TODO: Validate.
        query = {
            'configuration': query['configuration'],
            'stage': query['stage'],
            'url': query['url']
        }

        data = {
            '$push': {
                'versions': data
            }
        }

        return self.db.pages.update_one(query, data)
