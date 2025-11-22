import threading

from log import get_logger
from scrapers.default.cache import ScraperCache
from scrapers.default.client import ScraperConfiguration, ScraperClient
from scrapers.default.db import ScraperDb
from scrapers.default.queue import ScraperQueue
from scrapers.default.statistics import ScraperStatistics
from utils import get_configurations


logger = get_logger()


def process_pages(configuration, statistics):
    logger.info('Thread "%s" starting...', configuration['name'])

    cache = ScraperCache(directory='/data')
    db = ScraperDb(database='scraper')
    queue = ScraperQueue()

    scraper = ScraperClient(cache=cache, db=db, queue=queue, statistics=statistics)
    scraper.add_configuration(ScraperConfiguration(configuration))
    scraper.enable_parser()
    scraper.process()

    logger.info('Thread "%s" exiting...', configuration['name'])


def main():
    logger.info('Service starting...')

    try:
        statistics = ScraperStatistics()
        statistics = None

        threads = []

        for configuration in get_configurations():
            x = threading.Thread(target=process_pages, args=(configuration, statistics))
            x.start()

            threads.append(x)

        for thread in threads:
            thread.join()
    except KeyboardInterrupt as e:
        logger.warning('Processing stopped: %s', e)
    except Exception as e:
        logger.exception('Scraper failed: %s', e)

    logger.info('Service exiting...')


if __name__ == '__main__':
    main()
