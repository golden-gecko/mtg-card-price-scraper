import os
import pymongo.errors
import re
import time

from bs4 import BeautifulSoup

from log import get_logger
from mongo import MongoGatherer
from rabbit import RabbitClient
from utils import download_and_save_image, download_and_save_text, get_timestamp, load_file


class GathererClient:
    search_url = 'https://gatherer.wizards.com/Pages/Advanced.aspx'

    page_url = 'http://gatherer.wizards.com/Pages/Search/Default.aspx?page={page_id}&name=+[]'

    card_details_oracle_url = 'http://gatherer.wizards.com/Pages/Card/Details.aspx?printed=false&multiverseid={card_id}'
    card_details_printed_url = 'http://gatherer.wizards.com/Pages/Card/Details.aspx?printed=true&multiverseid={card_id}'
    card_image_url = 'http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid={card_id}&type=card'
    card_languages_url = 'http://gatherer.wizards.com/Pages/Card/Languages.aspx?multiverseid={card_id}'
    card_printings_url = 'http://gatherer.wizards.com/Pages/Card/Printings.aspx?multiverseid={card_id}'

    def __init__(self, mongo: MongoGatherer, rabbit: RabbitClient):
        self.mongo = mongo
        self.rabbit = rabbit

        self.logger = get_logger(__name__)

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
        while True:
            try:
                self.rabbit.connect()

                channel = self.rabbit.create_channel()
                channel.basic_qos(prefetch_count=10)

                channel.queue_declare(queue='gatherer_cards', durable=True)
                channel.queue_declare(queue='gatherer_cards_failed', durable=True)
                channel.queue_declare(queue='gatherer_pages', durable=True)
                channel.queue_declare(queue='gatherer_pages_failed', durable=True)

                channel.basic_consume(queue='gatherer_cards', on_message_callback=self.process_card)
                channel.basic_consume(queue='gatherer_pages', on_message_callback=self.process_page)

                try:
                    channel.start_consuming()
                except KeyboardInterrupt as e:
                    self.logger.warning('Processing interrupted: %s', e)
                    channel.cancel()
                    channel.stop_consuming()
                    self.rabbit.disconnect()
                    break
            except Exception as e:
                self.logger.critical('Processing failed: %s', e)
                self.rabbit.disconnect()

                time.sleep(1)

    def _validate_id(self, value):
        try:
            value = value.decode('utf-8')
            value = int(value)
        except ValueError as e:
            self.logger.error('Value is not valid: %s', e)

            return None
        else:
            return value

    def _get_page_text(self, page_id):
        file_name = os.path.join('/', 'data', 'pages', '{}.html'.format(page_id))
        text = self._load_cache(file_name)

        if not text:
            self.logger.debug('Page not cached. Downloading...')

            text = download_and_save_text(self.page_url.format(page_id=page_id), file_name)

            if not text:
                self.logger.error('Failed to download page %d', page_id)
                return
        else:
            self.logger.debug('Page cached. Fetching from cache...')

        return text

    def is_flip_card(self, soup):
        side_1 = '#ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_ctl02_nameRow'
        side_2 = '#ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_ctl03_nameRow'
        side_3 = '#ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_ctl04_nameRow'

        flipped_1 = soup.select_one(side_1) and soup.select_one(side_2)
        flipped_2 = soup.select_one(side_2) and soup.select_one(side_3)

        if flipped_1:
            return '_ctl02', '_ctl03'

        if flipped_2:
            return '_ctl03', '_ctl04'

        return None

    def process_card(self, channel, method_frame, header_frame, body):
        self.logger.debug('Received card message: %s', body)

        card_id = self._validate_id(body)

        if card_id is None:
            self.logger.error('Failed to process card %d', card_id)
            self.queue_card(card_id=card_id, queue_name='gatherer_cards_failed')
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return

        self.logger.debug('Processing card %d', card_id)

        # skip of card was processed
        if self.is_card_processed(card_id):
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return

        # download card details oracle
        details_oracle_file_name = os.path.join('/', 'data', 'cards', 'details', 'oracle', '{}.html'.format(card_id))
        details_oracle_html = self._load_cache(details_oracle_file_name)

        if not details_oracle_html:
            self.logger.debug('Card details oracle not cached. Downloading...')

            details_oracle_html = download_and_save_text(self.card_details_oracle_url.format(card_id=card_id), details_oracle_file_name)

            if not details_oracle_html:
                self.logger.error('Failed to download card details oracle %d', card_id)
                channel.basic_nack(delivery_tag=method_frame.delivery_tag)
                return
        else:
            self.logger.debug('Card details oracle cached. Fetching from cache...')

        # download card details printed
        details_printed_file_name = os.path.join('/', 'data', 'cards', 'details', 'printed', '{}.html'.format(card_id))
        details_printed_html = self._load_cache(details_printed_file_name)

        if not details_printed_html:
            self.logger.debug('Card details printed not cached. Downloading...')

            details_printed_html = download_and_save_text(self.card_details_printed_url.format(card_id=card_id), details_printed_file_name)

            if not details_printed_html:
                self.logger.error('Failed to download card details printed %d', card_id)
                self.queue_card(card_id=card_id, queue_name='gatherer_cards_failed')
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return
        else:
            self.logger.debug('Card details printed cached. Fetching from cache...')

        # download card image
        image_file_name = os.path.join('/', 'data', 'cards', 'images', '{}.png'.format(card_id))

        if not self._is_cache_available(image_file_name):
            self.logger.debug('Card image not cached. Downloading...')

            image = download_and_save_image(self.card_image_url.format(card_id=card_id), image_file_name)

            if not image:
                self.logger.error('Downloading card image %d failed', card_id)
                self.queue_card(card_id=card_id, queue_name='gatherer_cards_failed')
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return
        else:
            self.logger.debug('Card image cached. Fetching from cache...')

        # download card languages
        languages_file_name = os.path.join('/', 'data', 'cards', 'languages', '{}.html'.format(card_id))
        languages_html = self._load_cache(languages_file_name)

        if not languages_html:
            self.logger.debug('Card languages not cached. Downloading...')

            languages_html = download_and_save_text(self.card_languages_url.format(card_id=card_id), languages_file_name)

            if not languages_html:
                self.logger.error('Downloading languages %d failed', card_id)
                self.queue_card(card_id=card_id, queue_name='gatherer_cards_failed')
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return
        else:
            self.logger.debug('Card languages cached. Fetching from cache...')

        # download card printings
        printing_file_name = os.path.join('/', 'data', 'cards', 'printings', '{}.html'.format(card_id))
        printings_html = self._load_cache(printing_file_name)

        if not printings_html:
            self.logger.debug('Card printings not cached. Downloading...')

            printings_html = download_and_save_text(self.card_printings_url.format(card_id=card_id), printing_file_name)

            if not printings_html:
                self.logger.error('Downloading printings %d failed', card_id)
                self.queue_card(card_id=card_id, queue_name='gatherer_cards_failed')
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return
        else:
            self.logger.debug('Card printings cached. Fetching from cache...')

        details_oracle_soup = BeautifulSoup(details_oracle_html, 'html.parser')
        details_printed_soup = BeautifulSoup(details_printed_html, 'html.parser')
        languages_soup = BeautifulSoup(languages_html, 'html.parser')
        printings_soup = BeautifulSoup(printings_html, 'html.parser')

        # validate downloaded pages
        if not details_oracle_soup.select_one('#ctl00_ctl00_ctl00_MainContent_SubContent_SubContentHeader_subtitleDisplay'):
            self.logger.error('Fetch details oracle are invalid for card %d', card_id)
            self._delete_cache(details_oracle_file_name)
            self.queue_card(card_id=card_id, queue_name='gatherer_cards_failed')
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return

        if not details_printed_soup.select_one('#ctl00_ctl00_ctl00_MainContent_SubContent_SubContentHeader_subtitleDisplay'):
            self.logger.error('Fetch details printed are invalid for card %d', card_id)
            self._delete_cache(details_printed_file_name)
            self.queue_card(card_id=card_id, queue_name='gatherer_cards_failed')
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return

        # create data object
        data = {
            'card_id': card_id,
            'timestamp': get_timestamp()
        }

        # check if card is flip card
        prefixes = self.is_flip_card(details_oracle_soup)

        if prefixes:
            self.logger.debug('Card %d is flip card', card_id)

            # process card details oracle
            oracle = self._process_details(details_oracle_soup, prefixes[0])

            if not oracle:
                self.logger.error('Failed to process card %d details oracle', card_id)
                self.queue_card(card_id=card_id, queue_name='gatherer_cards_failed')
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return

            data['oracle'] = oracle

            # process card details printed
            printed = self._process_details(details_printed_soup, prefixes[0])

            if not printed:
                self.logger.error('Failed to process card %d details printed', card_id)
                self.queue_card(card_id=card_id, queue_name='gatherer_cards_failed')
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return

            data['printed'] = printed

            # process card details oracle (flipped)
            oracle_flipped = self._process_details(details_oracle_soup, prefixes[1])

            if not oracle_flipped:
                self.logger.error('Failed to process card %d details oracle', card_id)
                self.queue_card(card_id=card_id, queue_name='gatherer_cards_failed')
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return

            data['oracle_flipped'] = oracle_flipped

            # process card details printed (flipped)
            printed_flipped = self._process_details(details_printed_soup, prefixes[1])

            if not printed_flipped:
                self.logger.error('Failed to process card %d details printed', card_id)
                self.queue_card(card_id=card_id, queue_name='gatherer_cards_failed')
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return

            data['printed_flipped'] = printed_flipped
        else:
            self.logger.debug('Card %d is normal card', card_id)

            # process card details oracle
            self.logger.debug('Processing card details oracle')
            oracle = self._process_details(details_oracle_soup)

            if not oracle:
                self.logger.error('Failed to process card %d details oracle', card_id)
                self.queue_card(card_id=card_id, queue_name='gatherer_cards_failed')
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return

            data['oracle'] = oracle

            # process card details printed
            self.logger.debug('Processing card details printed')
            printed = self._process_details(details_printed_soup)

            if not printed:
                self.logger.error('Failed to process card %d details printed', card_id)
                self.queue_card(card_id=card_id, queue_name='gatherer_cards_failed')
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                return

            data['printed'] = printed

        # process card languages
        languages = {}

        no_languages = languages_soup.select_one('#ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_languageList_noOtherLanguagesParent')

        if not no_languages:
            for x in languages_soup.select('.cardList .cardItem'):
                translated_name = x.select_one('td:nth-child(1)')
                language = x.select_one('td:nth-child(2)')
                translated_language = x.select_one('td:nth-child(3)')

                if not translated_name or not language or not translated_language:
                    self.logger.error('Language in invalid format for card %d', card_id)
                    self.queue_card(card_id=card_id, queue_name='gatherer_cards_failed')
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                    return

                translated_name = translated_name.text.strip()
                language = language.text.strip()
                translated_language = translated_language.text.strip()

                if not translated_name or not language or not translated_language:
                    self.logger.error('Language in invalid format for card %d', card_id)
                    self.queue_card(card_id=card_id, queue_name='gatherer_cards_failed')
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                    return

                languages[language] = {
                    'name': translated_name,
                    'language': translated_language
                }

        if languages:
            data['languages'] = languages

        # process card printings
        formats = {}

        no_formats = printings_soup.select_one('#ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_LegalityList_zeroItems')

        if not no_formats:
            for x in printings_soup.select('.cardList:nth-child(4) .cardItem'):
                name = x.select_one('td:nth-child(1)')
                legality = x.select_one('td:nth-child(2)')

                if not name or not legality:
                    self.logger.error('Format in invalid format for card %d', card_id)
                    self.queue_card(card_id=card_id, queue_name='gatherer_cards_failed')
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                    return

                name = name.text.strip()
                legality = legality.text.strip()

                if not name or not legality:
                    self.logger.error('Format in invalid format for card %d', card_id)
                    self.queue_card(card_id=card_id, queue_name='gatherer_cards_failed')
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                    return

                formats[name] = legality

        if formats:
            data['formats'] = formats

        # process card variations
        variations = []

        for x in details_oracle_soup.select('#ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_variationLinks .variationLink'):
            if x.has_attr('id'):
                try:
                    variation_card_id = int(x['id'])
                except ValueError as e:
                    self.logger.warning('ID is not a number: %s', e)
                else:
                    variations.append(variation_card_id)
                    self.queue_card(card_id=variation_card_id)
            else:
                self.logger.warning('No ID in variation: %s', x)

        if variations:
            data['variations'] = variations

        # index card
        try:
            self.mongo.index_card(data)
        except pymongo.errors.DuplicateKeyError as e:
            self.logger.warning('card %d already indexed: %s', card_id, e)

        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def process_page(self, channel, method_frame, header_frame, body):
        self.logger.debug('Received page message: %s', body)

        page_id = self._validate_id(body)

        if page_id is None:
            self.logger.error('Failed to process page %d', page_id)
            self.queue_page(page_id=page_id, queue_name='gatherer_pages_failed')
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return

        self.logger.debug('Processing page %d', page_id)

        # skip if page was processed
        if self.is_page_processed(page_id):
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
            self.queue_page(page_id=page_id, queue_name='gatherer_pages_failed')
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return

        # process page
        soup = BeautifulSoup(text, 'html.parser')

        # process page - get other pages
        pages = soup.select('#ctl00_ctl00_ctl00_MainContent_SubContent_topPagingControlsContainer a')
        self.logger.debug('Found %d pages', len(pages))

        for page in pages:
            match = re.match(r'/Pages/Search/Default.aspx\?page=(?P<page_id>\d+)&name=\+\[\]', page['href'])

            if match:
                self.queue_page(page_id=int(match.group('page_id')))

        # process page - get cards
        cards = soup.select('.cardItem a')
        self.logger.debug('Found %d cards', len(cards))

        for card in cards:
            match = re.match(r'\.\./Card/Details\.aspx\?multiverseid=(?P<card_id>\d+)', card['href'])

            if match:
                self.queue_card(card_id=int(match.group('card_id')))

        # index page
        try:
            self.mongo.index_page(data)
        except pymongo.errors.DuplicateKeyError as e:
            self.logger.warning('Page %d already indexed: %s', page_id, e)

        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def process_search(self) -> bool:
        self.logger.debug('Processing search form')

        file_name = os.path.join('/', 'data', 'search.html')
        text = self._load_cache(file_name)

        if not text:
            self.logger.debug('Search form not cached. Downloading...')

            text = download_and_save_text(self.search_url, file_name)

            if not text:
                self.logger.error('Failed to download search form')
                return True

        soup = BeautifulSoup(text, 'html.parser')

        blocks = self._extract_options(soup, '#ctl00_ctl00_MainContent_Content_blockRow a')
        colors = self._extract_options(soup, '#ctl00_ctl00_MainContent_Content_colorRow a')
        expansions = self._extract_options(soup, '#ctl00_ctl00_MainContent_Content_setRow a')
        formats = self._extract_options(soup, '#ctl00_ctl00_MainContent_Content_formatRow a')
        subtypes = self._extract_options(soup, '#ctl00_ctl00_MainContent_Content_subtypeRow a')
        types = self._extract_options(soup, '#ctl00_ctl00_MainContent_Content_typeRow a')

        self.logger.debug(blocks)
        self.logger.debug(colors)
        self.logger.debug(expansions)
        self.logger.debug(formats)
        self.logger.debug(subtypes)
        self.logger.debug(types)

        self.mongo.delete_blocks()
        self.mongo.delete_colors()
        self.mongo.delete_expansions()
        self.mongo.delete_formats()
        self.mongo.delete_subtypes()
        self.mongo.delete_types()

        for item in blocks:
            if not self.mongo.index_block(item):
                return False

        for item in expansions:
            if not self.mongo.index_expansion(item):
                return False

        for item in colors:
            if not self.mongo.index_color(item):
                return False

        for item in formats:
            if not self.mongo.index_format(item):
                return False

        for item in subtypes:
            if not self.mongo.index_subtype(item):
                return False

        for item in types:
            if not self.mongo.index_type(item):
                return False

        return True

    def queue_card(self, card_id: int, queue_name='gatherer_cards') -> bool:
        if self.is_card_processed(card_id=card_id):
            return True

        self.logger.debug('Queuing card %d', card_id)
        self.rabbit.connect()
        channel = self.rabbit.create_channel()
        response = self.rabbit.send(channel=channel, queue_name=queue_name, value=str(card_id))
        self.rabbit.disconnect()

        if response:
            return True

        return False

    def queue_page(self, page_id: int, queue_name='gatherer_pages') -> bool:
        if self.is_page_processed(page_id=page_id):
            return True

        self.logger.debug('Queuing page %d', page_id)
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
    def _is_cache_available(file_name: str) -> bool:
        return os.path.exists(file_name)

    @staticmethod
    def _load_cache(file_name: str):
        if not os.path.exists(file_name):
            return False

        return load_file(file_name)

    def _get_selector(self, name: str, prefix: str = '', ) -> str:
        return '#ctl00_ctl00_ctl00_MainContent_SubContent_SubContent{}_{}Row'.format(prefix, name)

    def _extract_attribute(self, soup, selector: str, name: str, data: dict, prefix: str = ''):
        # self.logger.debug('Searching for attribute "%s" using selector "%s" and prefix "%s"', name, selector, prefix)

        s = '{} .value'.format(self._get_selector(selector, prefix))
        # self.logger.debug('s: %s', s)

        attribute = soup.select_one(s)
        # self.logger.debug('attribute: %s', attribute)

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

    def _process_details(self, soup: BeautifulSoup, prefix: str = ''):
        data = {}

        # extract name
        self._extract_attribute(soup, 'name', 'name', data, prefix)

        if 'name' not in data:
            self.logger.warning('Card name not found')
            return None

        # extract mana
        mana = []

        for x in soup.select('{} .value img'.format(self._get_selector('mana', prefix))):
            mana.append(x['alt'].strip())

        if mana:
            data['mana'] = mana

        # extract converted mana cost
        self._extract_attribute(soup, 'cmc', 'converted_mana_cost', data, prefix)

        if 'converted_mana_cost' in data:
            data['converted_mana_cost'] = data['converted_mana_cost']

        # extract type
        self._extract_attribute(soup, 'type', 'type', data, prefix)

        # extract text
        text = []

        for x in soup.select('{} .cardtextbox'.format(self._get_selector('text', prefix))):
            for y in x.descendants:
                if y.name == 'img':
                    text.append(y['alt'])
                elif y.name is None:
                    if y.strip():
                        text.append(y.strip())
                    else:
                        self.logger.warning('Text compontent is empty')
                else:
                    self.logger.warning('Unsupported text compontent: %s', y.name)

        if text:
            data['text'] = text

        # extract flavor
        flavor = []

        for x in soup.select('{} .flavortextbox'.format(self._get_selector('flavor', prefix))):
            flavor.append(x.text.strip())

        if flavor:
            data['flavor'] = flavor

        # extract watermark
        self._extract_attribute(soup, 'mark', 'watermark', data, prefix)

        # extract power, toughness or loyalty
        self._extract_attribute(soup, 'pt', 'power', data, prefix)

        pt = soup.select_one('{}'.format(self._get_selector('pt', prefix)))

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
        self._extract_attribute(soup, 'set', 'set', data, prefix)

        # extract rarity
        self._extract_attribute(soup, 'rarity', 'rarity', data, prefix)

        # extract other sets
        other_sets = []

        for x in soup.select('{} .value a'.format('otherSets', prefix)):
            match = re.match(r'Details\.aspx\?multiverseid=(?P<number>\d+)', x['href'])

            if match:
                other_set_card_id = int(match.group('number'))
                other_sets.append(other_set_card_id)
                self.queue_card(card_id=other_set_card_id)

        if other_sets:
            data['other_sets'] = other_sets

        # extract number
        self._extract_attribute(soup, 'number', 'number', data, prefix)

        # extract artist
        self._extract_attribute(soup, 'artist', 'artist', data, prefix)

        return data
