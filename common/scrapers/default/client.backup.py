import json
import pymongo.errors
import random

from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlunsplit

from log import get_logger
from scrapers.default.cache import ScraperCache
from scrapers.default.db import ScraperDb
from scrapers.default.exceptions import ScraperDuplicateException, ScraperProcessingException, ScraperSkipException
from scrapers.default.queue import ScraperQueue
from utils import download, ExecutionTime, ExpirationTime, get_timestamp, wait


class ScraperPage:
    def __init__(self, db: ScraperDb, task: dict):
        self.logger = get_logger()

        self.db = db
        self.task = task
        self.data = None

        if not {'configuration', 'stage', 'url'}.issubset(task.keys()):
            raise ScraperProcessingException('Failed to validate task')

    def get_from_db(self) -> None:
        if not self.data:
            self.data = self.db.has_page(self.task['configuration'], self.task['stage'], self.task['url'])

    def is_version_indexed(self, cache_path):
        return self.db.has_version(cache_path)


class ScraperClient:
    def __init__(self, cache: ScraperCache, db: ScraperDb, queue: ScraperQueue):
        self.logger = get_logger()

        self.cache = cache
        self.db = db
        self.queue = queue

        self.configurations = []

    def add_configuration(self, configuration: dict):
        self.configurations.append(configuration)

    def get_step_expire_time(self, configuration: dict, stage_name: str):
        self.logger.debug('configuration: %s', configuration)
        self.logger.debug('stage_name: %s', stage_name)

        for stage in configuration['stages']:
            if stage['name'] == stage_name:
                return stage['expires'] if 'expires' in stage else ExpirationTime.month

        raise ScraperProcessingException('Stage "{}" not found'.format(stage_name))

    def register_configurations(self):
        for configuration in self.configurations:
            self.logger.info('Registering configuration "%s"...', configuration['name'])

            queue_name = 'scraper_{}'.format(configuration['name'])

            self.queue.add_callback(queue_name, self.process_tasks)

            for stage in configuration['stages']:
                self.logger.debug('stage: %s', stage)

                for step in stage['steps']:
                    if 'urls' in step:
                        expires = self.get_step_expire_time(configuration, step['stage'])

                        for url in step['urls']:
                            self.queue_url(queue_name, step['stage'], url, expires)

    def process(self):
        self.logger.info('Processing starting...')

        while True:
            try:
                self.queue.connect()
                self.register_configurations()
                self.queue.start_consuming()
            except KeyboardInterrupt as e:
                self.logger.warning('Processing stopped: %s', e)
                self.queue.disconnect()

                break
            except Exception as e:
                self.logger.exception('Processing failed: %s', e)
                self.queue.disconnect()

                wait(1.0)

    def download_url(self, prefix, url, expiration_time):
        url_html, url_path, url_timestamp = self.cache.get(prefix, url, expiration_time)
        url_code = None
        url_download_time = None

        if url_html:
            self.logger.debug('Page "%s" found in cache (%d)', url, expiration_time)
        else:
            self.logger.warning('Page "%s" not found in cache (%d)', url, expiration_time)

            url_html, url_code, url_download_time = download(url)

            if url_html:
                self.logger.debug('Page "%s" downloaded', url)

                url_path, url_timestamp = self.cache.set(prefix, url, url_html)
            else:
                raise ScraperProcessingException('Failed to download page "{}"'.format(url))

        return url_html, url_code, url_path, url_timestamp, url_download_time

    def get_configuration_by_name(self, name: str) -> [dict, None]:
        for configuration in self.configurations:
            if configuration['name'] == name:
                return configuration

        return None

    def validate_configuration(self, queue_name: str) -> tuple:
        configuration_name = queue_name.replace('scraper_', '', 1)
        configuration = self.get_configuration_by_name(configuration_name)

        if not configuration:
            raise ScraperProcessingException('Configuration "%s" not found', configuration_name)

        return configuration_name, configuration

    def validate_task(self, task):
        if 'stage' not in task:
            raise ScraperProcessingException('Key "stage" not found in task')

        if 'url' not in task:
            raise ScraperProcessingException('Key "url" not found in task')

        if 'expires' not in task:
            task['expires'] = ExpirationTime.month

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

    def process_selector(self, soup, base_url, stage_name, selector, queue_name, expires):
        sub_urls_elements = soup.select(selector)

        self.logger.debug('Found %d sub URL-s', len(sub_urls_elements))

        sub_urls = []

        for url in sub_urls_elements:
            if url.has_attr('href'):
                sub_urls.append(self.validate_url(base_url, url['href']))
            else:
                self.logger.warning('No "href" attribute in "%s"', url)

        random.shuffle(sub_urls)

        for url in sub_urls:
            self.queue_url(queue_name, stage_name, url, expires)

    def process_tasks(self, channel, method_frame, header_frame, body):
        with ExecutionTime('Processing page'):
            queue_name = method_frame.routing_key

            self.logger.debug('Received message "%s" from queue "%s"', body, queue_name)

            body_json = body.decode('utf-8')
            body_json = json.loads(body_json)

            try:
                configuration_name, configuration = self.validate_configuration(queue_name)

                task = self.validate_task(body_json)
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
                with ExecutionTime('Indexing page'):
                    try:
                        self.db.index_page(data)
                    except pymongo.errors.DuplicateKeyError as e:
                        self.logger.warning('Page is already indexed: %s', e)

                with ExecutionTime('Downloading page'):
                    url_html, url_code, cache_path, cache_timestamp, url_download_time = self.download_url(
                        configuration_name, task['url'], task['expires']
                    )
                    url_soup = BeautifulSoup(url_html, 'lxml')

                    stats = {
                        'code': url_code,
                        'configuration': configuration_name,
                        'stage': task['stage'],
                        'timestamp': get_timestamp(),
                        'url': task['url'],
                    }

                    if url_download_time:
                        stats['download_time'] = url_download_time
                        stats['cache'] = False
                    else:
                        stats['cache'] = True

                    self.db.index_stats(stats)

                page = ScraperPage(self.db, task)

                with ExecutionTime('Search for version'):
                    if page.is_version_indexed(cache_path):
                        raise ScraperSkipException('Version is indexed. Skipping...')

                attributes = {}

                for sub_configuration in configuration[task['stage']]:
                    self.logger.debug('sub_configuration: %s', sub_configuration)

                    if 'attributes' in sub_configuration:
                        self.process_attributes(url_soup, task['url'], sub_configuration['attributes'], attributes)

                    if 'stage' in sub_configuration and 'selector' in sub_configuration:
                        self.process_selector(
                            url_soup,
                            task['url'],
                            sub_configuration['stage'],
                            sub_configuration['selector'],
                            method_frame.routing_key,
                            sub_configuration['expires']
                        )

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
                self.logger.exception('Failed to process task: %s', e)

                body_json['error'] = str(e)

                self.queue_value('{}_failed'.format(queue_name), json.dumps(body_json))
            finally:
                self.queue.ack(method_frame.delivery_tag)

    def queue_url(self, queue, stage, url, expires):
        self.logger.debug('ScraperClient.queue_url(%s, %s, %s, %s)', queue, stage, url, expires)
        self.logger.info('Queuing "%s" URL', url)

        data = {
            'stage': stage,
            'url': url,
            'expires': expires
        }

        self.queue.publish(queue, json.dumps(data))

    def queue_value(self, queue, value):
        self.queue.publish(queue, value)
