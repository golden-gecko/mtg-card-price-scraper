import json
import jsonschema
import random

from bs4 import BeautifulSoup
from pymongo.errors import DuplicateKeyError
from urllib.parse import urlsplit, urlunsplit

from log import get_logger
from scrapers.default import schemas
from scrapers.default.cache import ScraperCache
from scrapers.default.db import ScraperDb
from scrapers.default.exceptions import ScraperDuplicateException, ScraperProcessingException, ScraperSkipException
from scrapers.default.queue import ScraperQueue
from utils import download, ExecutionTime, get_default_expiration_time, get_queue_name, get_timestamp, load_file, wait


class ScraperConfiguration:
    def __init__(self, configuration: dict):
        self.logger = get_logger()

        self.configuration = configuration

    def get_expire_time(self, stage_name: str) -> int:
        stage = self.get_stage(stage_name)

        return stage['expires'] if 'expires' in stage else get_default_expiration_time()

    def get_stage(self, stage_name: str) -> dict:
        for stage in self.get_stages():
            if stage['name'] == stage_name:
                return stage

        raise ScraperProcessingException('Stage "{}" not found'.format(stage_name))

    def get_stages(self) -> list:
        return self.configuration['stages']

    def get_name(self) -> str:
        return self.configuration['name']


class ScraperPage:
    def __init__(self, db: ScraperDb, task: dict):
        self.logger = get_logger()

        self.db = db
        self.task = task
        self.data = None

        if not {'configuration', 'stage', 'url'}.issubset(task.keys()):
            raise ScraperProcessingException('Failed to validate task')

    def get_from_db(self):
        if not self.data:
            self.data = self.db.has_page(self.task['configuration'], self.task['stage'], self.task['url'])

    def is_version_indexed(self, cache_path: str):
        return self.db.has_version(cache_path)


class ScraperClient:
    def __init__(self, cache: ScraperCache, db: ScraperDb, queue: ScraperQueue):
        self.logger = get_logger()

        self.cache = cache
        self.db = db
        self.queue = queue

        self.configurations = []

    def add_configuration(self, configuration: ScraperConfiguration):
        self.logger.info('Adding configuration "%s"...', configuration.get_name())

        self.configurations.append(configuration)

    def register_configurations(self):
        for configuration in self.configurations:
            configuration_name = configuration.get_name()

            self.logger.debug('configuration_name: %s', configuration_name)

            self.queue.add_callback(get_queue_name(configuration_name, 'downloader'), self.process_downloaders)
            self.queue.add_callback(get_queue_name(configuration_name, 'parser'), self.process_parsers)
            self.queue.add_callback(get_queue_name(configuration_name, 'indexer'), self.process_indexers)

            for stage in configuration.get_stages():
                for step in stage['steps']:
                    if 'urls' in step:
                        expires = configuration.get_expire_time(step['stage'])

                        for url in step['urls']:
                            self.queue_url_for_downloading(configuration_name, step['stage'], url, expires)

    def get_configuration_by_name(self, name: str) -> ScraperConfiguration:
        for configuration in self.configurations:
            if configuration.get_name() == name:
                return configuration

        raise ScraperProcessingException('Failed to get "%s" configuration "{}"'.format(name))

    def process(self):
        self.logger.info('Processing starting...')

        retries = 0
        retries_max = 3

        while retries < retries_max:
            try:
                self.queue.connect()
                self.register_configurations()
                self.queue.start_consuming()

                retries = 0
            except KeyboardInterrupt as e:
                self.logger.warning('Processing stopped: %s', e)
                self.queue.disconnect()

                break
            except Exception as e:
                self.logger.exception('Processing failed (%d): %s', retries, e)
                self.queue.disconnect()

                retries += 1

                wait(1.0)

    def download_url(self, configuration: str, url: str, expires: int) -> dict:
        response = {
            'cache': None,
            'code': None,
            'download_time': None,
            'error': None,
            'html': None,
            'path': None,
            'timestamp': None
        }

        html, path, timestamp = self.cache.get(configuration, url, expires)

        response['html'] = html
        response['path'] = path

        if html:
            self.logger.debug('Page "%s" found in cache (%d)', url, expires)

            response['cache'] = True
        else:
            self.logger.warning('Page "%s" not found in cache (%d)', url, expires)

            html, code, download_time, error = download(url)

            response['code'] = code
            response['download_time'] = download_time
            response['error'] = error
            response['html'] = html

            if html:
                self.logger.debug('Page "%s" downloaded', url)

                path, timestamp = self.cache.set(configuration, url, html)

                response['cache'] = False
                response['path'] = path
            else:
                self.logger.error('Failed to download page "{}"'.format(url))

        response['timestamp'] = get_timestamp()

        return response

    @staticmethod
    def validate_url(base: str, url: str) -> str:
        base_scheme, base_netloc, _, _, _ = urlsplit(base)
        url_scheme, url_netloc, url_path, url_query, url_fragment = urlsplit(url)

        if not url_scheme:
            url = urlunsplit((base_scheme, base_netloc, url_path, url_query, url_fragment))

        return url

    def process_attributes(self, soup: BeautifulSoup, configuration_name: str, stage_name: str, url: str, cache_path: str, attributes: dict) -> dict:
        data = {}

        for name, selector in attributes.items():
            if callable(selector):
                self.logger.warning('Searching for attribute "%s"', name)

                value = selector(soup)

                if not value:
                    self.logger.warning('Attribute "%s" not found', name)
                else:
                    value = value.strip()

                    if not value:
                        self.logger.warning('Attribute "%s" found, but it is empty', name)
                    else:
                        data[name] = value
            else:
                self.logger.warning('Searching for attribute "%s" with selector "%s"', name, selector)

                value = soup.select_one(selector)

                if not value:
                    self.logger.warning('Attribute "%s" not found', name)
                else:
                    value = value.text.strip()

                    if not value:
                        self.logger.warning('Attribute "%s" found, but it is empty', name)
                    else:
                        data[name] = value

        if data:
            self.queue_attributes_for_indexing(configuration_name, stage_name, url, cache_path, data)

        return data

    def process_selector(self, soup: BeautifulSoup, configuration_name: str, stage_name: str, url: str, selector: str, expires: int):
        sub_urls_elements = soup.select(selector)

        self.logger.debug('Found %d sub URL-s', len(sub_urls_elements))

        sub_urls = []

        for sub_url in sub_urls_elements:
            if sub_url.has_attr('href'):
                sub_urls.append(self.validate_url(url, sub_url['href']))
            else:
                self.logger.warning('No "href" attribute in "%s"', sub_url)

        random.shuffle(sub_urls)

        for sub_url in sub_urls:
            self.queue_url_for_downloading(configuration_name, stage_name, sub_url, expires)

    def index_stats(self, configuration_name: str, body_json: dict, response: dict):
        stats = {
            'cache': response['cache'],
            'code': response['code'],
            'configuration': configuration_name,
            'download_time': response['download_time'],
            'error': response['error'],
            'expires': body_json['expires'],
            'stage': body_json['stage'],
            'timestamp': response['timestamp'],
            'url': body_json['url']
        }

        self.logger.debug('stats: %s', stats)

        self.db.index_stats(stats)

    def process_downloaders(self, channel, method_frame, header_frame, body):
        with ExecutionTime('Processing ({})'.format(method_frame.routing_key)):
            self.logger.debug('Received message "%s" from queue "%s"', body, method_frame.routing_key)

            body_json = body.decode('utf-8')
            body_json = json.loads(body_json)

            try:
                try:
                    jsonschema.validate(body_json, schemas.message_downloader)
                except jsonschema.ValidationError as e:
                    raise ScraperProcessingException(e)

                self.logger.debug('task: %s', body_json)

                configuration_name = body_json['configuration']
                configuration = self.get_configuration_by_name(configuration_name)

                self.logger.debug('configuration_name: %s', configuration_name)
                self.logger.debug('configuration: %s', configuration)

                with ExecutionTime('Downloading page'):
                    response = self.download_url(configuration_name, body_json['url'], body_json['expires'])

                    self.logger.debug('response: %s', response)

                    self.index_stats(configuration_name, body_json, response)

                    if response['html']:
                        self.queue_page_for_parsing(
                            configuration_name, body_json['stage'], body_json['url'], response['path']
                        )

                    self.logger.debug('Message processed')
            except Exception as e:
                self.logger.error('Failed to process task: %s', e)

                # body_json['error'] = str(e)

                self.queue_value('{}_failed'.format(method_frame.routing_key), body)
            finally:
                self.queue.ack(method_frame.delivery_tag)

    def process_parsers(self, channel, method_frame, header_frame, body):
        with ExecutionTime('Processing ({})'.format(method_frame.routing_key)):
            self.logger.debug('Received message "%s" from queue "%s"', body, method_frame.routing_key)

            body_json = body.decode('utf-8')
            body_json = json.loads(body_json)

            try:
                try:
                    jsonschema.validate(body_json, schemas.message_parser)
                except jsonschema.ValidationError as e:
                    raise ScraperProcessingException(e)

                configuration_name = body_json['configuration']
                configuration = self.get_configuration_by_name(configuration_name)

                stage_name = body_json['stage']
                stage = configuration.get_stage(stage_name)

                html = load_file(body_json['cache_path'])

                soup = BeautifulSoup(html, 'lxml')

                for step in stage['steps']:
                    if 'attributes' in step:
                        attributes = self.process_attributes(
                            soup, configuration_name, stage_name, body_json['url'], body_json['cache_path'], step['attributes']
                        )

                        self.logger.debug('attributes: %s', attributes)

                    if 'selectors' in step:
                        expires = configuration.get_expire_time(step['stage'])

                        for selector in step['selectors']:
                            self.process_selector(
                                soup, configuration_name, step['stage'], body_json['url'], selector, expires
                            )

                    if 'urls' in step:
                        expires = configuration.get_expire_time(step['stage'])

                        for url in step['urls']:
                            self.queue_url_for_downloading(configuration_name, step['stage'], url, expires)

                    self.logger.debug('Message processed')
            except Exception as e:
                self.logger.error('Failed to process task: %s', e)

                # body_json['error'] = str(e)

                self.queue_value('{}_failed'.format(method_frame.routing_key), body)
            finally:
                self.queue.ack(method_frame.delivery_tag)

    def process_indexers(self, channel, method_frame, header_frame, body):
        with ExecutionTime('Processing ({})'.format(method_frame.routing_key)):
            self.logger.debug('Received message "%s" from queue "%s"', body, method_frame.routing_key)

            body_json = body.decode('utf-8')
            body_json = json.loads(body_json)

            try:
                try:
                    jsonschema.validate(body_json, schemas.message_indexer)
                except jsonschema.ValidationError as e:
                    raise ScraperProcessingException(e)

                try:
                    self.db.index_page(body_json)
                except DuplicateKeyError as e:
                    self.logger.warn('Failed to index page: %s', e)

                self.logger.debug('Message processed')
            except Exception as e:
                self.logger.error('Failed to process task: %s', e)

                # body_json['error'] = str(e)

                self.queue_value('{}_failed'.format(method_frame.routing_key), body)
            finally:
                self.queue.ack(method_frame.delivery_tag)

    def queue_url_for_downloading(self, configuration: str, stage: str, url: str, expires: int):
        self.logger.info('Queuing for downloading %s, %s, %s, %s', configuration, stage, url, expires)

        data = {
            'configuration': configuration,
            'expires': expires,
            'stage': stage,
            'url': url
        }

        self.queue_value(get_queue_name(configuration, 'downloader'), json.dumps(data))

    def queue_page_for_parsing(self, configuration: str, stage: str, url: str, cache_path: str):
        self.logger.info('Queuing for parsing %s, %s, %s', configuration, stage, cache_path)

        data = {
            'cache_path': cache_path,
            'configuration': configuration,
            'stage': stage,
            'url': url
        }

        self.queue_value(get_queue_name(configuration, 'parser'), json.dumps(data))

    def queue_attributes_for_indexing(self, configuration: str, stage: str, url: str, cache_path: str, attributes: dict):
        self.logger.info('Queuing for indexing %s, %s, %s', configuration, stage, attributes)

        data = {
            'attributes': attributes,
            'cache_path': cache_path,
            'configuration': configuration,
            'stage': stage,
            'url': url
        }

        self.queue_value(get_queue_name(configuration, 'indexer'), json.dumps(data))

    def queue_value(self, queue, value):
        self.logger.debug('ScraperClient.queue_value(%s, %s)', queue, value)

        self.queue.publish(queue, value)
