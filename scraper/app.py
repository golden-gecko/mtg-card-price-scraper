from gatherer import GathererClient
from log import get_logger
from mongo import Mongo
from rabbit import RabbitClient


if __name__ == '__main__':
    logger = get_logger(__name__)
    logger.info('Scraper starting...')

    mongo = Mongo(host='mongo')
    rabbit = RabbitClient(host='rabbit')

    gatherer = GathererClient(mongo=mongo, rabbit=rabbit)
    # gatherer.process_search()
    gatherer.process()
