from pymongo import ASCENDING, MongoClient

from log import get_logger


class MongoGatherer:
    def __init__(self, host):
        self.client = MongoClient(host)

        self.db = self.client.gatherer
        self.db.cards.create_index([('card_id', ASCENDING)], unique=True)
        self.db.colors.create_index([('name', ASCENDING)], unique=True)
        self.db.formats.create_index([('name', ASCENDING)], unique=True)
        self.db.pages.create_index([('page_id', ASCENDING)], unique=True)
        self.db.sets.create_index([('name', ASCENDING)], unique=True)
        self.db.subtypes.create_index([('name', ASCENDING)], unique=True)
        self.db.types.create_index([('name', ASCENDING)], unique=True)

        self.logger = get_logger(__name__)

    def delete_blocks(self):
        return self.db.blocks.delete_many({})

    def delete_colors(self):
        return self.db.colors.delete_many({})

    def delete_expansions(self):
        return self.db.expansions.delete_many({})

    def delete_formats(self):
        return self.db.formats.delete_many({})

    def delete_subtypes(self):
        return self.db.subtypes.delete_many({})

    def delete_types(self):
        return self.db.types.delete_many({})

    def get_blocks(self):
        return self.db.blocks.find({}, {'_id': False}).sort('name', ASCENDING)

    def get_cards(self):
        return self.db.cards.find({}, {'_id': False}).sort('name', ASCENDING)

    def get_expansions(self):
        return self.db.expansions.find({}, {'_id': False}).sort('name', ASCENDING)

    def get_formats(self):
        return self.db.formats.find({}, {'_id': False}).sort('name', ASCENDING)

    def get_sets(self):
        return self.db.sets.find({}, {'_id': False}).sort('name', ASCENDING)

    def get_types(self):
        return self.db.types.find({}, {'_id': False}).sort('name', ASCENDING)

    def index_block(self, data) -> bool:
        return self.db.blocks.insert_one(data)

    def index_card(self, data) -> bool:
        return self.db.cards.insert_one(data)

    def index_color(self, data) -> bool:
        return self.db.colors.insert_one(data)

    def index_expansion(self, data) -> bool:
        return self.db.expansions.insert_one(data)

    def index_format(self, data) -> bool:
        return self.db.formats.insert_one(data)

    def index_page(self, data) -> bool:
        return self.db.pages.insert_one(data)

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


class MongoMagic:
    def __init__(self, host):
        self.client = MongoClient(host)

        self.db = self.client.magic
        self.db.blocks.create_index([('name', ASCENDING)], unique=True)
        self.db.expansions.create_index([('name', ASCENDING)], unique=True)
        self.db.formats.create_index([('name', ASCENDING)], unique=True)
        self.db.rarities.create_index([('name', ASCENDING)], unique=True)
        self.db.subtypes.create_index([('name', ASCENDING)], unique=True)
        self.db.supertypes.create_index([('name', ASCENDING)], unique=True)
        self.db.types.create_index([('name', ASCENDING)], unique=True)

        self.logger = get_logger(__name__)

    def delete_blocks(self):
        return self.db.blocks.delete_many({})

    def delete_expansions(self):
        return self.db.expansions.delete_many({})

    def delete_formats(self):
        return self.db.formats.delete_many({})

    def delete_rarities(self):
        return self.db.rarities.delete_many({})

    def delete_subtypes(self):
        return self.db.subtypes.delete_many({})

    def delete_supertypes(self):
        return self.db.supertypes.delete_many({})

    def delete_types(self):
        return self.db.types.delete_many({})

    def get_blocks(self):
        return self.db.blocks.find({}, {'_id': False}).sort('name', ASCENDING)

    def get_cards(self):
        return self.db.cards.find({}, {'_id': False}).sort('name', ASCENDING)

    def get_expansions(self):
        return self.db.expansions.find({}, {'_id': False}).sort('name', ASCENDING)

    def get_expansions_count(self):
        return self.db.expansions.count_documents({})

    def get_formats(self):
        return self.db.formats.find({}, {'_id': False}).sort('name', ASCENDING)

    def get_formats_count(self):
        return self.db.formats.count_documents({})

    def get_subtypes(self):
        return self.db.subtypes.find({}, {'_id': False}).sort('name', ASCENDING)

    def get_subtypes_count(self):
        return self.db.subtypes.count_documents({})

    def get_supertypes(self):
        return self.db.supertypes.find({}, {'_id': False}).sort('name', ASCENDING)

    def get_supertypes_count(self):
        return self.db.supertypes.count_documents({})

    def get_types(self):
        return self.db.types.find({}, {'_id': False}).sort('name', ASCENDING)

    def get_types_count(self):
        return self.db.types.count_documents({})

    def has_card(self, card_id: int) -> bool:
        return self.db.cards.find_one({'card_id': card_id})

    def has_page(self, page_id: int) -> bool:
        return self.db.pages.find_one({'page_id': page_id})

    def index_block(self, data) -> bool:
        return self.db.blocks.insert_one(data)

    def index_card(self, data) -> bool:
        return self.db.cards.insert_one(data)

    def index_expansion(self, data) -> bool:
        return self.db.expansions.insert_one(data)

    def index_format(self, data) -> bool:
        return self.db.formats.insert_one(data)

    def index_page(self, data) -> bool:
        return self.db.pages.insert_one(data)

    def index_subtype(self, data) -> bool:
        return self.db.subtypes.insert_one(data)

    def index_supertype(self, data) -> bool:
        return self.db.supertypes.insert_one(data)

    def index_type(self, data) -> bool:
        return self.db.types.insert_one(data)
