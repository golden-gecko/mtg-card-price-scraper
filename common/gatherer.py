import os
import pymongo.errors
import re
import time

from bs4 import BeautifulSoup

from log import get_logger
from mongo import Mongo
from rabbit import RabbitClient
from utils import download_and_save_image, download_and_save_text, get_timestamp, load_file


class GathererClient:
    search_url = 'http://gatherer.wizards.com/Pages/Default.aspx'

    page_url = 'http://gatherer.wizards.com/Pages/Search/Default.aspx?page={page_id}&name=+[]'

    card_details_oracle_url = 'http://gatherer.wizards.com/Pages/Card/Details.aspx?printed=false&multiverseid={card_id}'
    card_details_printed_url = 'http://gatherer.wizards.com/Pages/Card/Details.aspx?printed=true&multiverseid={card_id}'
    card_image_url = 'http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid={card_id}&type=card'
    card_printings_url = 'http://gatherer.wizards.com/Pages/Card/Printings.aspx?multiverseid={card_id}'

    def __init__(self, mongo: Mongo, rabbit: RabbitClient):
        self.mongo = mongo
        self.rabbit = rabbit

        self.logger = get_logger(__name__)

    def is_card_processed(self, card_id: int) -> bool:
        return self.mongo.has_card(card_id)

    def is_page_processed(self, page_id: int) -> bool:
        return self.mongo.has_page(page_id)

    def process(self):
        while True:
            try:
                self.rabbit.connect()

                channel = self.rabbit.create_channel()
                channel.basic_qos(prefetch_count=10)

                channel.queue_declare(queue='cards', durable=True)
                channel.queue_declare(queue='cards_failed', durable=True)
                channel.queue_declare(queue='pages', durable=True)
                channel.queue_declare(queue='pages_failed', durable=True)

                channel.basic_consume(queue='cards', on_message_callback=self.process_card)
                channel.basic_consume(queue='pages', on_message_callback=self.process_page)

                try:
                    channel.start_consuming()
                except KeyboardInterrupt as e:
                    self.logger.warning('Processing Gatherer stopped: %s', e)
                    channel.stop_consuming()
                    self.rabbit.disconnect()
                    break
            except Exception as e:
                self.logger.error('Processing Gatherer failed: %s', e)
                channel.stop_consuming()
                self.rabbit.disconnect()
                time.sleep(1)

    def _validate_id(self, value):
        try:
            value = value.decode('utf-8')
            value = int(value)
        except ValueError as e:
            self.logger.error(e)

            return None
        else:
            return value

    def _get_page_text(self, page_id):
        file_name = os.path.join('/', 'data', 'pages', '{}.html'.format(page_id))
        text = self._load_cache(file_name)

        if not text:
            self.logger.info('Page not cached. Downloading...')

            text = download_and_save_text(self.page_url.format(page_id=page_id), file_name)

            if not text:
                self.logger.error('Downloading page %d failed', page_id)
                return
        else:
            self.logger.info('Page cached. Fetching from cache...')

        return text

    def process_card(self, channel, method_frame, header_frame, body):
        self.logger.info('Received card message: %s', body)

        card_id = self._validate_id(body)

        if card_id is None:
            self.logger.error('Failed to process card %d', card_id)
            self.queue_card(card_id=card_id, queue_name='cards_failed')
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return

        self.logger.info('Processing card %d', card_id)

        # skip of card was processed
        if self.is_card_processed(card_id):
            self.logger.warning('Card %d already processed', card_id)
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return

        # create data object
        data = {
            'card_id': card_id,
            'timestamp': get_timestamp()
        }

        # download card details oracle
        file_name = os.path.join('/', 'data', 'cards', 'details', 'oracle', '{}.html'.format(card_id))
        text = self._load_cache(file_name)

        if not text:
            self.logger.info('Card details oracle not cached. Downloading...')

            text = download_and_save_text(self.card_details_oracle_url.format(card_id=card_id), file_name)

            if not text:
                self.logger.error('Downloading card details oracle %d failed', card_id)
                channel.basic_nack(delivery_tag=method_frame.delivery_tag)
                return
        else:
            self.logger.info('Card details oracle cached. Fetching from cache...')

        # process card details oracle
        oracle = self._process_details(text)

        if not oracle:
            self.logger.error('Failed to process card %d details oracle', card_id)
            self.queue_card(card_id=card_id, queue_name='cards_failed')
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return

        data['oracle'] = oracle

        # download card details printed
        file_name = os.path.join('/', 'data', 'cards', 'details', 'printed', '{}.html'.format(card_id))
        text = self._load_cache(file_name)

        if not text:
            self.logger.info('Card details printed not cached. Downloading...')

            text = download_and_save_text(self.card_details_printed_url.format(card_id=card_id), file_name)

            if not text:
                self.logger.error('Downloading card details printed %d failed', card_id)
                self.queue_card(card_id=card_id, queue_name='cards_failed')
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return
        else:
            self.logger.info('Card details printed cached. Fetching from cache...')

        # process card variations
        soup = BeautifulSoup(text, 'html.parser')

        variations = []

        for x in soup.select('#ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_variationLinks .variationLink'):
            if x.has_attr('id'):
                try:
                    id = int(x['id'])
                except ValueError as e:
                    self.logger.warning('ID is not a number: %s', e)
                else:
                    variations.append(id)
            else:
                self.logger.warning('No ID in variation: %s', x)

        if variations:
            data['variations'] = variations

        # process card details printed
        printed = self._process_details(text)

        if not printed:
            self.logger.error('Failed to process card %d details printed', card_id)
            self.queue_card(card_id=card_id, queue_name='cards_failed')
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return

        data['printed'] = printed

        # download card image
        file_name = os.path.join('/', 'data', 'cards', 'images', '{}.png'.format(card_id))

        if not self._is_cache_available(file_name):
            self.logger.info('Card image not cached. Downloading...')

            image = download_and_save_image(self.card_image_url.format(card_id=card_id), file_name)

            if not image:
                self.logger.error('Downloading card image %d failed', card_id)
                self.queue_card(card_id=card_id, queue_name='cards_failed')
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return
        else:
            self.logger.info('Card image cached. Fetching from cache...')

        # download card printings
        file_name = os.path.join('/', 'data', 'cards', 'printings', '{}.html'.format(card_id))
        text = self._load_cache(file_name)

        if not text:
            self.logger.info('Card printings not cached. Downloading...')

            text = download_and_save_text(self.card_printings_url.format(card_id=card_id), file_name)

            if not text:
                self.logger.error('Downloading printings %d failed', card_id)
                self.queue_card(card_id=card_id, queue_name='cards_failed')
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return
        else:
            self.logger.info('Card printings cached. Fetching from cache...')

        # process card printings
        soup = BeautifulSoup(text, 'html.parser')

        formats = {}

        no_formats = soup.select_one('#ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_LegalityList_zeroItems')

        if not no_formats:
            for x in soup.select('.cardList:nth-child(4) .cardItem'):
                name = x.select_one('td:nth-child(1)')
                legality = x.select_one('td:nth-child(2)')

                if not name or not legality:
                    self.logger.error('Format in invalid format for card %d', card_id)
                    self.queue_card(card_id=card_id, queue_name='cards_failed')
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                    return

                name = name.text.strip()
                legality = legality.text.strip()

                if not name or not legality:
                    self.logger.error('Format in invalid format for card %d', card_id)
                    self.queue_card(card_id=card_id, queue_name='cards_failed')
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                    return

                formats[name] = legality

        if formats:
            data['formats'] = formats

        self.logger.debug(data)

        # index card
        try:
            self.mongo.index_card(data)
        except pymongo.errors.DuplicateKeyError as e:
            self.logger.warning('Failed to index card: %s', e)

        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def process_page(self, channel, method_frame, header_frame, body):
        self.logger.info('Received page message: %s', body)

        page_id = self._validate_id(body)

        if page_id is None:
            self.logger.error('Failed to process page %d', page_id)
            self.queue_page(page_id=page_id, queue_name='pages_failed')
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return

        self.logger.info('Processing page %d', page_id)

        # skip if page was processed
        if self.is_page_processed(page_id):
            self.logger.warning('Page %d already processed', page_id)
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return

        # create data object
        data = {
            'page_id': page_id,
            'timestamp': get_timestamp()
        }

        # download page
        text = self._get_page_text(page_id)

        if not text:
            self.queue_page(page_id=page_id, queue_name='pages_failed')
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return

        # process page
        soup = BeautifulSoup(text, 'html.parser')

        # process page - get other pages
        pages = soup.select('#ctl00_ctl00_ctl00_MainContent_SubContent_topPagingControlsContainer a')
        self.logger.info('Found %d pages', len(pages))

        for page in pages:
            match = re.match(r'/Pages/Search/Default.aspx\?page=(?P<page_id>\d+)&name=\+\[\]', page['href'])

            if match:
                self.queue_page(page_id=int(match.group('page_id')))

        # process page - get cards
        cards = soup.select('.cardItem a')
        self.logger.info('Found %d cards', len(cards))

        for card in cards:
            match = re.match(r'\.\./Card/Details\.aspx\?multiverseid=(?P<card_id>\d+)', card['href'])

            if match:
                self.queue_card(card_id=int(match.group('card_id')))

        # index page
        try:
            self.mongo.index_page(data)
        except pymongo.errors.DuplicateKeyError as e:
            self.logger.warning('Failed to index page: %s', e)

        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def process_search(self):
        self.logger.info('Processing search form')

        file_name = os.path.join('/', 'data', 'search.html')
        text = self._load_cache(file_name)

        if not text:
            self.logger.info('Search form not cached. Downloading...')

            text = download_and_save_text(self.search_url, file_name)

            if not text:
                self.logger.error('Downloading search form failed')
                return

        soup = BeautifulSoup(text, 'html.parser')

        formats = self._extract_options(soup, '#ctl00_ctl00_MainContent_Content_SearchControls_formatAddText option')
        sets = self._extract_options(soup, '#ctl00_ctl00_MainContent_Content_SearchControls_setAddText option')
        types = self._extract_options(soup, '#ctl00_ctl00_MainContent_Content_SearchControls_typeAddText option')

        self.logger.debug(formats)
        self.logger.debug(sets)
        self.logger.debug(types)

        self.mongo.delete_formats()
        self.mongo.delete_sets()
        self.mongo.delete_types()

        for format in formats:
            self.mongo.index_format(format)

        for set in sets:
            self.mongo.index_set(set)

        for type in types:
            self.mongo.index_type(type)

    def queue_card(self, card_id: int, queue_name='cards') -> bool:
        self.logger.info('Queuing card %d', card_id)

        if self.is_card_processed(card_id=card_id):
            return True

        self.rabbit.connect()
        channel = self.rabbit.create_channel()
        response = self.rabbit.send(channel=channel, queue_name=queue_name, value=str(card_id))
        self.rabbit.disconnect()

        if response:
            return True

        return False

    def queue_page(self, page_id: int, queue_name='pages') -> bool:
        self.logger.info('Queuing page %d', page_id)

        if self.is_page_processed(page_id=page_id):
            return True

        self.rabbit.connect()
        channel = self.rabbit.create_channel()
        response = self.rabbit.send(channel=channel, queue_name=queue_name, value=str(page_id))
        self.rabbit.disconnect()

        if response:
            return True

        return False

    @staticmethod
    def _delete_cache(file_name):
        if os.path.exists(file_name):
            os.remove(file_name)

    @staticmethod
    def _extract_attribute(soup, selector: str, name: str, data: dict):
        attribute = soup.select_one('#ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_{}Row .value'.format(selector))

        if attribute:
            data[name] = attribute.text.strip()

    def _extract_options(self, soup, selector):
        values = soup.select(selector)
        names = []

        for value in values:
            name = value.text.strip()

            if name:
                names.append({'name': name})

        return names

    @staticmethod
    def _is_cache_available(file_name: str) -> bool:
        return os.path.exists(file_name)

    @staticmethod
    def _load_cache(file_name: str):
        if not os.path.exists(file_name):
            return False

        return load_file(file_name)

    def _process_details(self, text):
        data = {}

        # process card details printed
        soup = BeautifulSoup(text, 'html.parser')

        # extract name
        self._extract_attribute(soup, 'name', 'name', data)

        # extract mana
        mana = []

        for x in soup.select('#ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_manaRow .value img'):
            mana.append(x['alt'])

        if mana:
            data['mana'] = mana

        # extract converted mana cost
        self._extract_attribute(soup, 'cmc', 'converted_mana_cost', data)

        if 'converted_mana_cost' in data:
            data['converted_mana_cost'] = int(data['converted_mana_cost'])

        # extract type
        self._extract_attribute(soup, 'type', 'type', data)

        # extract text
        text = []

        for x in soup.select('#ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_textRow .cardtextbox'):
            for y in x.descendants:
                if y.name == 'img':
                    text.append(y['alt'])
                elif y.name is None:
                    text.append(y.strip())
                else:
                    self.logger.warning('Unsupported text compontent: %s %s', y.name, y)

        if text:
            data['text'] = text

        # extract flavor
        flavor = []

        for x in soup.select('#ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_flavorRow .flavortextbox'):
            flavor.append(x.text.strip())

        if flavor:
            data['flavor'] = flavor

        # extract watermark
        self._extract_attribute(soup, 'mark', 'watermark', data)

        # extract power, toughness or loyalty
        self._extract_attribute(soup, 'pt', 'power', data)

        pt = soup.select_one('#ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_ptRow')

        if pt:
            pt_label = pt.select_one('.label')
            pt_value = pt.select_one('.value')

            if not pt_label or not pt_value:
                self.logger.error('Power / Toughness has no label or value')
                return False

            pt_label = pt_label.text.strip()
            pt_value = pt_value.text.strip()

            if not pt_label or not pt_value:
                self.logger.error('Power / Toughness has empty label or value')
                return False

            if pt_label == 'P/T:':
                pt_value = pt_value.split(' / ')

                if len(pt_value) != 2:
                    self.logger.error('Power / Toughness has invalid format')
                    return False

                data['power'] = pt_value[0]
                data['toughness'] = pt_value[1]
            elif pt_label == 'Loyalty:':
                data['loyalty'] = pt_value

        # extract set
        self._extract_attribute(soup, 'set', 'set', data)

        # extract rarity
        self._extract_attribute(soup, 'rarity', 'rarity', data)

        # extract other sets
        other_sets = []

        for x in soup.select('#ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_otherSetsRow .value a'):
            match = re.match(r'Details\.aspx\?multiverseid=(?P<number>\d+)', x['href'])

            if match:
                other_sets.append(int(match.group('number')))
                self.queue_card(card_id=int(match.group('number')))

        if other_sets:
            data['other_sets'] = other_sets

        # extract number
        self._extract_attribute(soup, 'number', 'number', data)

        # extract artist
        self._extract_attribute(soup, 'artist', 'artist', data)

        return data
