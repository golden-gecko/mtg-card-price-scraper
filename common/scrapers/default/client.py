import datetime
import json
import pymongo.errors
import time

from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlunsplit

from log import get_logger, log_call
from scrapers.default.cache import ScraperCache
from scrapers.default.db import ScraperDb
from scrapers.default.exception import ScraperDuplicateException, ScraperProcessingException, ScraperSkipException
from scrapers.default.queue import ScraperQueue
from utils import download, get_timestamp


class ScraperPage:
    def __init__(self, db: ScraperDb, task: dict):
        self.logger = get_logger(__name__)

        self.db = db
        self.task = task
        self.data = None

        if not {'configuration', 'stage', 'url'}.issubset(task.keys()):
            raise ScraperProcessingException('Failed to validate task')

    def get_from_db(self) -> None:
        if not self.data:
            self.data = self.db.has_page(self.task['configuration'], self.task['stage'], self.task['url'])

    def is_version_indexed(self, cache_path, cache_timestamp) -> bool:
        
        return True

    """
    def has_to_refresh(self) -> bool:
        self.get_from_db()

        if 'versions' not in self.data:
            self.logger.warning('No versions in page. Refreshing...')
            return True

        if not len(self.data['versions']):
            self.logger.warning('Empty versions in page. Refreshing...')
            return True

        if 'refresh' not in self.task:
            self.logger.warning('Page is not queued to refresh. Refreshing...')
            return False

        if not self.task['refresh']:
            self.logger.warning('Page is not queued to refresh. Refreshing...')
            return False

        def sort(x):
            if 'cache' not in x:
                raise ScraperProcessingException('Key "cache" not found in x')

            if 'timestamp' not in x['cache']:
                raise ScraperProcessingException('Key "timestamp" not found in cache')

            return x['cache']['timestamp']

        versions = sorted(self.data['versions'], key=sort, reverse=True)
        version_time = datetime.datetime.strptime(versions[0]['cache']['timestamp'], '%Y-%m-%dT%H:%M:%S.%f')

        now = datetime.datetime.utcnow()

        if (now - version_time).total_seconds() < 3600:
            self.logger.warning('Version is fresh. Not refreshing')
            return False

        return True
    """


class ScraperClient:
    def __init__(self, cache: ScraperCache, db: ScraperDb, queue: ScraperQueue):
        self.logger = get_logger(__name__)

        self.cache = cache
        self.db = db
        self.queue = queue

        self.configurations = {}

    def add_configuration(self, name, configuration):
        self.configurations[name] = configuration

    def process(self):
        self.logger.info('Processing starting...')

        while True:
            try:
                self.queue.connect()

                for configuration_name, configuration in self.configurations.items():
                    self.logger.debug(configuration_name)
                    self.logger.debug(configuration)

                    self.queue.add_callback('scraper_{}'.format(configuration_name), self.process_tasks)

                    for _, tasks in configuration.items():
                        for task in tasks:
                            if 'stage' in task and 'url' in task:
                                self.queue_url('scraper_{}'.format(configuration_name), task['stage'], task['url'])

                self.queue.start_consuming()
            except KeyboardInterrupt as e:
                self.logger.warning('Processing interrupted: %s', e)
                self.queue.disconnect()

                break
            except Exception as e:
                self.logger.critical('Processing failed: %s', e)
                self.queue.disconnect()

                time.sleep(1)

    def download_url(self, prefix, url):
        url_html, url_path, url_timestamp = self.cache.get(prefix, url)

        if url_html:
            self.logger.debug('Page "%s" found in cache', url)
        else:
            self.logger.warning('Page "%s" not found in cache', url)

            url_html = download(url)

            if url_html:
                self.logger.debug('Page "%s" downloaded', url)

                url_path, url_timestamp = self.cache.set(prefix, url, url_html)
            else:
                raise ScraperProcessingException('Failed to download page "{}"'.format(url))

        return url_html, url_path, url_timestamp

    def validate_configuration(self, queue_name):
        configuration_name = queue_name.routing_key.replace('scraper_', '', 1)

        if configuration_name not in self.configurations:
            raise ScraperProcessingException('Task "%s" not found', configuration_name)

        return configuration_name, self.configurations[configuration_name]

    def validate_task(self, task):
        task = task.decode('utf-8')
        task = json.loads(task)

        if 'stage' not in task:
            raise ScraperProcessingException('Key "stage" not found in task')

        if 'url' not in task:
            raise ScraperProcessingException('Key "url" not found in task')

        if 'refresh' not in task or task['refresh'] not in (False, True):
            task['refresh'] = False

        return task

    def validate_url(self, base, url):
        base_scheme, base_netloc, _, _, _ = urlsplit(base)
        url_scheme, url_netloc, url_path, url_query, url_fragment = urlsplit(url)

        if not url_scheme:
            url = urlunsplit((base_scheme, base_netloc, url_path, url_query, url_fragment))

        return url

    def process_attributes(self, soup, url, attributes, data):
        for name, selector in attributes.items():
            value = soup.select_one(selector)

            if not value:
                self.logger.warning('Attribute "%s" not found in "%s" URL', name, url)
            else:
                value = value.text.strip()

                if not value:
                    self.logger.warning('Attribute "%s" found in "%s" URL, but it is empty', name, url)
                else:
                    data[name] = value

        self.logger.debug('Found attributes: %s', data)

        return data

    def process_selector(self, soup, base_url, stage_name, selector, queue_name):
        sub_urls = soup.select(selector)

        self.logger.debug('Found %d sub URL-s', len(sub_urls))

        for url in sub_urls:
            if url.has_attr('href'):
                url = self.validate_url(base_url, url['href'])

                self.queue_url(queue_name, stage_name, url)
            else:
                self.logger.warning('No "href" attribute in "%s"', url)

    def process_tasks(self, channel, method_frame, header_frame, body):
        self.logger.debug('Received message "%s" from queue "%s"', body, method_frame.routing_key)

        try:
            configuration_name, configuration = self.validate_configuration(method_frame)

            task = self.validate_task(body)
            task['configuration'] = configuration_name

            self.logger.debug('configuration_name: %s', configuration_name)
            self.logger.debug('configuration: %s', configuration)
            self.logger.debug('task: %s', task)

            if task['stage'] not in configuration:
                raise ScraperProcessingException('Stage "{}" not found in configuration'.format(task['stage']))

            data = {
                'configuration': configuration_name,
                'stage': task['stage'],
                'timestamp': get_timestamp(),
                'url': task['url']
            }

            # index page
            try:
                self.db.index_page(data)
            except pymongo.errors.DuplicateKeyError as e:
                self.logger.warning('Page is already indexed: %s', e)

            url_html, cache_path, cache_timestamp = self.download_url(configuration_name, task['url'])
            url_soup = BeautifulSoup(url_html, 'html.parser')

            page = ScraperPage(self.db, task)

            if page.is_version_indexed(cache_path, cache_timestamp):
                raise ScraperSkipException('Version is indexed. Skipping...')

            attributes = {}

            for sub_configuration in configuration[task['stage']]:
                self.logger.debug('sub_configuration: %s', sub_configuration)

                if 'attributes' in sub_configuration:
                    self.process_attributes(url_soup, task['url'], sub_configuration['attributes'], attributes)

                if 'stage' in sub_configuration and 'selector' in sub_configuration:
                    self.process_selector(url_soup, task['url'], sub_configuration['stage'], sub_configuration['selector'], method_frame.routing_key)

            version = {
                'cache': {
                    'path': cache_path,
                    'timestamp': cache_timestamp
                }
            }

            if attributes:
                version['attributes'] = attributes

            # index version
            self.db.index_version(task, version)
        except (ScraperDuplicateException, ScraperSkipException) as e:
            self.logger.warning('%s', e)
        except Exception as e:
            self.logger.debug('Failed to process task: %s', e)

            self.queue_value('{}_failed'.format(method_frame.routing_key), body)
        finally:
            self.queue.ack(method_frame.delivery_tag)

    def queue_url(self, queue, stage, url):
        self.logger.warning('Queuing "%s" URL', url)

        data = {
            'stage': stage,
            'url': url
        }

        self.queue.publish(queue, json.dumps(data))

    def queue_value(self, queue, value):
        self.queue.publish(queue, value)
