from log import get_logger
from scrapers.default.cache import ScraperCache
from scrapers.default.client import ScraperClient
from scrapers.default.db import ScraperDb
from scrapers.default.queue import ScraperQueue


if __name__ == '__main__':
    logger = get_logger(__name__)
    logger.info('Service starting...')

    gatherer = {
        'init': [
            {
                'stage': 'main',
                'url': 'http://gatherer.wizards.com/Pages/Search/Default.aspx?page=1&name=+[]'
            }
        ]
    }

    try:
        scraper = ScraperClient(ScraperCache('/data'), ScraperDb('mongo', 'gatherer'), ScraperQueue('rabbit'))
        scraper.add_configuration('gatherer', gatherer)
        scraper.process()
    except Exception as e:
        logger.critical('Scraper failed: %s', e)

    logger.info('Service exiting...')
