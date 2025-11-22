import threading

from log import get_logger
from scrapers.gatherer.client import GathererClient
from scrapers.gatherer.db import GathererDb
from scrapers.gatherer.queue import GathererQueue


logger = get_logger()


def process_search():
    db = GathererDb(host='mongo')

    queue = GathererQueue(host='rabbit')
    queue.connect()

    gatherer = GathererClient(db=db, queue=queue)
    gatherer.process_search()


def process_cards():
    logger.info('Thread %s starting...')

    db = GathererDb(host='mongo')

    queue = GathererQueue(host='rabbit')
    queue.connect()

    gatherer = GathererClient(db=db, queue=queue)
    gatherer.process_cards()

    logger.info('Thread %s exiting...')


def process_pages():
    logger.info('Thread %s starting...')

    db = GathererDb(host='mongo')

    queue = GathererQueue(host='rabbit')
    queue.connect()

    gatherer = GathererClient(db=db, queue=queue)
    gatherer.process_pages()

    logger.info('Thread %s exiting...')


def main():
    logger.info('Service starting...')

    try:
        # process_search()

        threads = []

        x = threading.Thread(target=process_cards)
        x.start()

        threads.append(x)

        x = threading.Thread(target=process_pages)
        x.start()

        threads.append(x)

        for thread in threads:
            thread.join()
    except KeyboardInterrupt as e:
        logger.warning('Processing stopped: %s', e)
    except Exception as e:
        logger.critical('Scraper failed: %s', e)

    logger.info('Service exiting...')


if __name__ == '__main__':
    main()
