from gatherer import GathererClient
from log import get_logger
from magic import MagicClient
from mongo import MongoGatherer, MongoMagic
from rabbit import RabbitClient


if __name__ == '__main__':
    logger = get_logger(__name__)
    logger.info('Service starting...')

    mongo = MongoGatherer(host='mongo')
    rabbit = RabbitClient(host='rabbit')

    gatherer = GathererClient(mongo=mongo, rabbit=rabbit)
    # gatherer.process_search()
    gatherer.process()

    # mongo = MongoMagic(host='mongo')
    # rabbit = RabbitClient(host='rabbit')

    # magic = MagicClient(mongo=mongo, rabbit=rabbit)
    # magic.process()

    logger.info('Service exiting...')
