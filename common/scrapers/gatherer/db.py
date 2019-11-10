from pymongo import ASCENDING, MongoClient

from log import get_logger


class GathererDb:
    def __init__(self, host):
        self.logger = get_logger()

        self.client = MongoClient(host)

        self.db = self.client.gatherer
        self.db.artists.create_index([('name', ASCENDING)], unique=True)
        self.db.blocks.create_index([('name', ASCENDING)], unique=True)
        self.db.cards.create_index([('card_id', ASCENDING)], unique=True)
        self.db.colors.create_index([('name', ASCENDING)], unique=True)
        self.db.formats.create_index([('name', ASCENDING)], unique=True)
        self.db.pages.create_index([('page_id', ASCENDING)], unique=True)
        self.db.rarities.create_index([('name', ASCENDING)], unique=True)
        self.db.subtypes.create_index([('name', ASCENDING)], unique=True)
        self.db.types.create_index([('name', ASCENDING)], unique=True)
        self.db.watermarks.create_index([('name', ASCENDING)], unique=True)

    def delete_blocks(self):
        return self.db.blocks.delete_many({})

    def delete_colors(self):
        return self.db.colors.delete_many({})

    def delete_formats(self):
        return self.db.formats.delete_many({})

    def delete_rarities(self):
        return self.db.rarities.delete_many({})

    def delete_sets(self):
        return self.db.sets.delete_many({})

    def delete_subtypes(self):
        return self.db.subtypes.delete_many({})

    def delete_types(self):
        return self.db.types.delete_many({})

    def get_artists(self) -> list:
        return list(self.db.artists.find({}, {'_id': 0}).sort('name', ASCENDING))

    def get_blocks(self) -> list:
        return list(self.db.blocks.find({}, {'_id': 0}).sort('name', ASCENDING))

    def get_card(self, card_id: int) -> dict:
        query = {
            'card_id': card_id
        }

        projection = {
            '_id': 0
        }

        return self.db.cards.find_one(query, projection)

    def get_cards(self, params=None, page: int = 0, limit: int = 10) -> list:
        query = {
        }

        if not ('all_versions' in params and params['all_versions']):
            query['main'] = True

        if 'artist' in params and params['artist']:
            query['oracle.artist'] = params['artist']

        """
        if 'block' in params and params['block']:
            query['oracle.block'] = params['block']
        """

        if 'color' in params and params['color']:
            query['oracle.mana'] = params['color']

        """
        if 'format' in params and params['format']:
            query['oracle.format'] = params['format']
        """

        if 'name' in params and params['name']:
            query['oracle.name'] = params['name']

        if 'number' in params and params['number']:
            query['oracle.number'] = params['number']

        if 'power' in params and params['power']:
            query['oracle.power'] = params['power']

        if 'rarity' in params and params['rarity']:
            query['oracle.rarity'] = params['rarity']

        if 'set' in params and params['set']:
            query['oracle.set'] = params['set']

        if 'subtype' in params and params['subtype']:
            query['oracle.subtypes'] = params['subtype']

        if 'toughness' in params and params['toughness']:
            query['oracle.toughness'] = params['toughness']

        if 'type' in params and params['type']:
            query['oracle.type'] = params['type']

        if 'watermark' in params and params['watermark']:
            query['oracle.watermark'] = params['watermark']

        projection = {
            '_id': 0
        }

        self.logger.debug('query: %s', query)
        self.logger.debug('projection: %s', projection)

        return list(
            self.db.cards
                .find(query, projection)
                .sort('name', ASCENDING)
                .skip(page * limit)
                .limit(limit)
        )

    def get_colors(self) -> list:
        return list(self.db.colors.find({}, {'_id': 0}).sort('name', ASCENDING))

    def get_formats(self) -> list:
        return list(self.db.formats.find({}, {'_id': 0}).sort('name', ASCENDING))

    def get_rarities(self) -> list:
        return list(self.db.rarities.find({}, {'_id': 0}).sort('name', ASCENDING))

    def get_sets(self) -> list:
        return list(self.db.sets.find({}, {'_id': 0}).sort('name', ASCENDING))

    def get_subtypes(self) -> list:
        return list(self.db.subtypes.find({}, {'_id': 0}).sort('name', ASCENDING))

    def get_types(self) -> list:
        return list(self.db.types.find({}, {'_id': 0}).sort('name', ASCENDING))

    def get_watermarks(self) -> list:
        return list(self.db.watermarks.find({}, {'_id': 0}).sort('name', ASCENDING))

    def index_artist(self, data) -> bool:
        return self.db.artists.insert_one(data)

    def index_attribute(self, value, collection):
        return self.db[collection].insert_one(value)

    def index_block(self, data) -> bool:
        return self.db.blocks.insert_one(data)

    def index_card(self, data) -> bool:
        if 'card_id' not in data:
            return False

        query = {
            'card_id': data['card_id']
        }

        if 'oracle' not in data:
            raise Exception('Key "oracle" not found')

        if 'other_sets' in data['oracle']:
            if data['card_id'] == max(data['oracle']['other_sets']):
                data['main'] = True
            else:
                data['main'] = False
        else:
            data['main'] = True

        return self.db.cards.update(query, data, upsert=True)

    def index_color(self, data) -> bool:
        return self.db.colors.insert_one(data)

    def index_format(self, data) -> bool:
        return self.db.formats.insert_one(data)

    def index_rarity(self, data) -> bool:
        return self.db.rarities.insert_one(data)

    def index_page(self, data) -> bool:
        if 'page_id' not in data:
            return False

        query = {
            'page_id': data['page_id']
        }

        return self.db.pages.update(query, data, upsert=True)

    def index_set(self, data) -> bool:
        return self.db.sets.insert_one(data)

    def index_subtype(self, data) -> bool:
        return self.db.subtypes.insert_one(data)

    def index_type(self, data) -> bool:
        return self.db.types.insert_one(data)

    def has_card(self, card_id: int) -> bool:
        return self.db.cards.find_one({'card_id': card_id})

    def has_page(self, page_id: int) -> bool:
        return self.db.pages.find_one({'page_id': page_id})
