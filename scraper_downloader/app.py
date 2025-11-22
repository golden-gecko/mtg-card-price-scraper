import threading

from configurations import cardmarket, cardstore, centrum_mtg, channelfireball, e_legion, flamberg, futurex, \
    gamesmasters, morigal, mtgstore, planeswalker, strefamtg
from log import get_logger
from scrapers.default.cache import ScraperCache
from scrapers.default.client import ScraperConfiguration, ScraperClient
from scrapers.default.db import ScraperDb
from scrapers.default.queue import ScraperQueue


logger = get_logger()


def process_pages(configuration):
    logger.info('Thread "%s" starting...', configuration['name'])

    cache = ScraperCache(directory='/data')
    db = ScraperDb(database='scraper')
    queue = ScraperQueue()

    scraper = ScraperClient(cache=cache, db=db, queue=queue)
    scraper.add_configuration(ScraperConfiguration(configuration))
    scraper.enable_downloader()
    scraper.process()

    logger.info('Thread "%s" exiting...', configuration['name'])


def main():
    logger.info('Service starting...')

    try:
        configurations = []

        configurations += cardmarket.configurations
        configurations += cardstore.configurations
        configurations += centrum_mtg.configurations
        configurations += channelfireball.configurations
        configurations += e_legion.configurations
        configurations += flamberg.configurations
        configurations += futurex.configurations
        configurations += gamesmasters.configurations
        configurations += morigal.configurations
        configurations += mtgstore.configurations
        configurations += planeswalker.configurations
        configurations += strefamtg.configurations

        threads = []

        for configuration in configurations:
            x = threading.Thread(target=process_pages, args=(configuration, ))
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
