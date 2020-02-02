import json
import jsonschema
import pymongo.errors
import random

from bs4 import BeautifulSoup
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

    def process_attributes(self, soup: BeautifulSoup, attributes: dict) -> dict:
        data = {}

        for name, selector in attributes.items():
            if callable(selector):
                self.logger.warning('Searching for attribute "%s"', name)

                data[name] = selector(soup)
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

        return data

    def process_selector(self, soup: BeautifulSoup, base_url: str, stage_name: str, selector: str, configuration_name: str, expires: int):
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
            self.queue_url_for_downloading(configuration_name, stage_name, url, expires)

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
                            configuration_name, body_json['stage'], response['path'], body_json['url']
                        )

                    self.logger.debug('Message processed')
            except (ScraperDuplicateException, ScraperSkipException) as e:
                self.logger.warning('%s', e)
            except Exception as e:
                self.logger.exception('Failed to process task: %s', e)

                body_json['error'] = str(e)

                self.queue_value('{}_failed'.format(method_frame.routing_key), json.dumps(body_json))
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
                    attributes = {}

                    if 'attributes' in step:
                        attributes = self.process_attributes(soup, step['attributes'])

                        self.logger.debug('attributes: %s', attributes)

                    if 'selectors' in step:
                        expires = configuration.get_expire_time(step['stage'])

                        for selector in step['selectors']:
                            self.process_selector(
                                soup, body_json['parent_url'], step['stage'], selector, configuration_name, expires
                            )

                    if 'urls' in step:
                        expires = configuration.get_expire_time(step['stage'])

                        for url in step['urls']:
                            self.queue_url_for_downloading(configuration_name, step['stage'], url, expires)

                '''
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
                '''
            except (ScraperDuplicateException, ScraperSkipException) as e:
                self.logger.warning('%s', e)
            except Exception as e:
                self.logger.exception('Failed to process task: %s', e)

                body_json['error'] = str(e)

                self.queue_value('{}_failed'.format(method_frame.routing_key), json.dumps(body_json))
            finally:
                self.queue.ack(method_frame.delivery_tag)

    def process_indexers(self, channel, method_frame, header_frame, body):
        with ExecutionTime('Processing ({})'.format(method_frame.routing_key)):
            self.logger.debug('Received message "%s" from queue "%s"', body, method_frame.routing_key)

            body_json = body.decode('utf-8')
            body_json = json.loads(body_json)

            try:
                pass
            except (ScraperDuplicateException, ScraperSkipException) as e:
                self.logger.warning('%s', e)
            except Exception as e:
                self.logger.exception('Failed to process task: %s', e)

                body_json['error'] = str(e)

                self.queue_value('{}_failed'.format(method_frame.routing_key), json.dumps(body_json))
            finally:
                self.queue.ack(method_frame.delivery_tag)

    """
    def process_tasks(self, channel, method_frame, header_frame, body):
        with ExecutionTime('Processing page'):
            queue_name = method_frame.routing_key

            self.logger.debug('Received message "%s" from queue "%s"', body, queue_name)

            body_json = body.decode('utf-8')
            body_json = json.loads(body_json)

            try:
                configuration_name, configuration = self.validate_configuration(queue_name)

                task = self.validate_task(body_json)

                self.logger.debug('configuration_name: %s', configuration_name)
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
    """

    def queue_url_for_downloading(self, configuration: str, stage: str, url: str, expires: int):
        self.logger.info('Queuing for downloading %s, %s, %s, %s', configuration, stage, url, expires)

        data = {
            'configuration': configuration,
            'expires': expires,
            'stage': stage,
            'url': url
        }

        self.queue_value(get_queue_name(configuration, 'downloader'), json.dumps(data))

    def queue_page_for_parsing(self, configuration: str, stage: str, cache_path: str, parent_url: str):
        self.logger.info('Queuing for parsing %s, %s, %s', configuration, stage, cache_path)

        data = {
            'configuration': configuration,
            'cache_path': cache_path,
            'parent_url': parent_url,
            'stage': stage,
        }

        self.queue_value(get_queue_name(configuration, 'parser'), json.dumps(data))

    def queue_value(self, queue, value):
        self.logger.debug('ScraperClient.queue_value(%s, %s)', queue, value)

        self.queue.publish(queue, value)
