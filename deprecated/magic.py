import time

from helpers import send_get
from log import get_logger
from mongo import MongoMagic
from rabbit import RabbitClient


def validate_card_id(value):
    try:
        value = int(value)
    except ValueError:
        return None
    else:
        if value <= 0:
            return None

        return value


def validate_page_id(value):
    try:
        value = int(value)
    except ValueError:
        return None
    else:
        if value < 0:
            return None

        return value


class MagicClient:
    base_url = 'https://api.magicthegathering.io/v1'

    def __init__(self, mongo: MongoMagic, rabbit: RabbitClient):
        self.mongo = mongo
        self.rabbit = rabbit

        self.logger = get_logger()

    def is_card_processed(self, card_id: int) -> bool:
        status = self.mongo.has_card(card_id)

        if status:
            self.logger.warning('Card %d already processed', card_id)

        return status

    def is_page_processed(self, page_id: int) -> bool:
        status = self.mongo.has_page(page_id)

        if status:
            self.logger.warning('Page %d already processed', page_id)

        return status

    def process(self):
        if not self.mongo.get_formats_count():
            self.process_formats()

        if not self.mongo.get_sets_count():
            self.process_sets()

        if not self.mongo.get_subtypes_count():
            self.process_subtypes()

        if not self.mongo.get_supertypes_count():
            self.process_supertypes()

        if not self.mongo.get_types_count():
            self.process_types()

        while True:
            try:
                self.rabbit.connect()

                channel = self.rabbit.create_channel()
                channel.basic_qos(prefetch_count=10)

                channel.queue_declare(queue='magic_cards', durable=True)
                channel.queue_declare(queue='magic_cards_failed', durable=True)
                channel.queue_declare(queue='magic_pages', durable=True)
                channel.queue_declare(queue='magic_pages_failed', durable=True)

                channel.basic_consume(queue='magic_cards', on_message_callback=self.process_card)
                channel.basic_consume(queue='magic_pages', on_message_callback=self.process_page)

                channel.start_consuming()
            except KeyboardInterrupt as e:
                self.logger.warning('Processing stopped: %s', e)
                break
            except Exception as e:
                self.logger.exception('Processing failed: %s', e)
                time.sleep(1)

    def process_formats(self) -> bool:
        response = send_get(url='{}/formats'.format(self.base_url))

        if response.status_code != 200:
            return False

        for item in response.json()['formats']:
            data = {
                'name': item
            }

            if not self.mongo.index_format(data):
                return False

        return True

    def process_sets(self) -> bool:
        response = send_get(url='{}/sets'.format(self.base_url))

        if response.status_code != 200:
            return False

        for item in response.json()['sets']:
            dictionary = {
                'block': 'block',
                'code': 'code',
                'name': 'name',
                'releaseDate': 'release_date'
            }

            data = {}

            for src, dst in dictionary.items():
                if src in item:
                    data[dst] = item[src]

            if not self.mongo.index_set(data):
                return False

        return True

    def process_subtypes(self) -> bool:
        response = send_get(url='{}/subtypes'.format(self.base_url))

        if response.status_code != 200:
            return False

        for item in response.json()['subtypes']:
            data = {
                'name': item
            }

            if not self.mongo.index_subtype(data):
                return False

        return True

    def process_supertypes(self) -> bool:
        response = send_get(url='{}/supertypes'.format(self.base_url))

        if response.status_code != 200:
            return False

        for item in response.json()['supertypes']:
            data = {
                'name': item
            }

            if not self.mongo.index_supertype(data):
                return False

        return True

    def process_types(self) -> bool:
        response = send_get(url='{}/types'.format(self.base_url))

        if response.status_code != 200:
            return False

        for item in response.json()['types']:
            data = {
                'name': item
            }

            if not self.mongo.index_type(data):
                return False

        return True

    def process_card(self, channel, method_frame, header_frame, body):
        self.logger.debug('Received card message: %s', body)

        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def process_page(self, channel, method_frame, header_frame, body):
        self.logger.debug('Received page message: %s', body)

        page_id = validate_page_id(body.decode('utf-8'))

        if page_id is None:
            self.queue_page(page_id=page_id, queue_name='magic_pages_failed')
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return

        response = send_get(url='{}/cards?page={}'.format(self.base_url, page_id))

        if response.status_code != 200:
            self.queue_page(page_id=page_id, queue_name='magic_pages_failed')
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return

        for item in response.json()['cards']:
            dictionary = {
                'name': 'name',
                'manaCost': 'mana_cost',
                'cmc': 'converted_mana_cost',
                'colors': 'colors',
                'colorIdentity': 'color_identity',
                'type': 'type',
                'supertypes': 'supertypes',
                'types': 'types',
                'rarity': 'rarity',
                'set': 'set',
                'text': 'text',
                'artist': 'artist',
                'number': 'number',
                'multiverseid': 'multiverse_id',
                'rulings': 'rulings',
                'foreignNames': 'foreign_names',
                'printings': 'printings',
                'originalText': 'original_text',
                'originalType': 'original_type',
                'legalities': 'legalities'
            }

            data = {}

            for src, dst in dictionary.items():
                if src in item:
                    data[dst] = item[src]

            if not self.mongo.index_card(data):
                self.queue_page(page_id=page_id, queue_name='magic_pages_failed')
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return

        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def queue_card(self, card_id: int, queue_name='magic_cards') -> bool:
        if self.is_card_processed(card_id=card_id):
            return True

        self.logger.debug('Queuing card %d', card_id)
        channel = self.rabbit.create_channel()
        response = self.rabbit.send(channel=channel, queue_name=queue_name, value=str(card_id))

        if response:
            return True

        return False

    def queue_page(self, page_id: int, queue_name='magic_pages') -> bool:
        if self.is_page_processed(page_id=page_id):
            return True

        self.logger.debug('Queuing page %d', page_id)
        channel = self.rabbit.create_channel()
        response = self.rabbit.send(channel=channel, queue_name=queue_name, value=str(page_id))

        if response:
            return True

        return False
