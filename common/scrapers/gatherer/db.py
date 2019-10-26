from pymongo import ASCENDING, MongoClient
from typing import List

from log import get_logger


class GathererDb:
    def __init__(self, host):
        self.logger = get_logger()

        self.client = MongoClient(host)

        self.db = self.client.gatherer
        self.db.blocks.create_index([('name', ASCENDING)], unique=True)
        self.db.cards.create_index([('card_id', ASCENDING)], unique=True)
        self.db.colors.create_index([('name', ASCENDING)], unique=True)
        self.db.formats.create_index([('name', ASCENDING)], unique=True)
        self.db.pages.create_index([('page_id', ASCENDING)], unique=True)
        self.db.rarities.create_index([('name', ASCENDING)], unique=True)
        self.db.subtypes.create_index([('name', ASCENDING)], unique=True)
        self.db.types.create_index([('name', ASCENDING)], unique=True)

    def delete_blocks(self):
        return self.db.blocks.delete_many({})

    def delete_colors(self):
        return self.db.colors.delete_many({})

    def delete_expansions(self):
        return self.db.expansions.delete_many({})

    def delete_formats(self):
        return self.db.formats.delete_many({})

    def delete_rarities(self):
        return self.db.rarities.delete_many({})

    def delete_subtypes(self):
        return self.db.subtypes.delete_many({})

    def delete_types(self):
        return self.db.types.delete_many({})

    def get_blocks(self) -> List:
        return list(self.db.blocks.find({}, {'_id': 0}).sort('name', ASCENDING))

    def get_cards(self, name: str = '', page: int = 0, limit: int = 10) -> List:
        query = {
            'main': True
        }

        if name:
            query['oracle.name'] = name

        projection = {
            '_id': 0,
            'card_id': 1,
            'oracle.name': 1,
            'oracle.rarity': 1,
            'oracle.set': 1,
            'oracle.type': 1
        }

        return list(
            self.db.cards.find(query, projection)
                .sort('name', ASCENDING)
                .skip(page * limit)
                .limit(limit)
        )

    def get_colors(self) -> List:
        return list(self.db.colors.find({}, {'_id': 0}).sort('name', ASCENDING))

    def get_expansions(self) -> List:
        return list(self.db.expansions.find({}, {'_id': 0}).sort('name', ASCENDING))

    def get_formats(self) -> List:
        return list(self.db.formats.find({}, {'_id': 0}).sort('name', ASCENDING))

    def get_rarities(self) -> List:
        return list(self.db.rarities.find({}, {'_id': 0}).sort('name', ASCENDING))

    def get_subtypes(self) -> List:
        return list(self.db.subtypes.find({}, {'_id': 0}).sort('name', ASCENDING))

    def get_types(self) -> List:
        return list(self.db.types.find({}, {'_id': 0}).sort('name', ASCENDING))

    def index_block(self, data) -> bool:
        return self.db.blocks.insert_one(data)

    def index_card(self, data) -> bool:
        if 'card_id' not in data:
            return False

        query = {
            'card_id': data['card_id']
        }

        if 'oracle' in data and 'other_sets' in data['oracle']:
            if data['card_id'] == max(data['oracle']['other_sets']):
                data['main'] = True

        return self.db.cards.update(query, data, upsert=True)

    def index_color(self, data) -> bool:
        return self.db.colors.insert_one(data)

    def index_expansion(self, data) -> bool:
        return self.db.expansions.insert_one(data)

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

    def index_subtype(self, data) -> bool:
        return self.db.subtypes.insert_one(data)

    def index_type(self, data) -> bool:
        return self.db.types.insert_one(data)

    def has_card(self, card_id: int) -> bool:
        return self.db.cards.find_one({'card_id': card_id})

    def has_page(self, page_id: int) -> bool:
        return self.db.pages.find_one({'page_id': page_id})
