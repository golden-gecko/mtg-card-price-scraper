from pymongo import ASCENDING, MongoClient

from log import get_logger


class Mongo:
    def __init__(self, host):
        self.client = MongoClient(host)
        self.db = self.client.gatherer

        self.logger = get_logger(__name__)

    def delete_formats(self):
        return self.db.formats.delete_many({})

    def delete_sets(self):
        return self.db.sets.delete_many({})

    def delete_types(self):
        return self.db.types.delete_many({})

    def get_cards(self):
        return self.db.cards.find({}, {'_id': False}).sort('name', ASCENDING)

    def get_formats(self):
        return self.db.formats.find({}, {'_id': False}).sort('name', ASCENDING)

    def get_sets(self):
        return self.db.sets.find({}, {'_id': False}).sort('name', ASCENDING)

    def get_types(self):
        return self.db.types.find({}, {'_id': False}).sort('name', ASCENDING)

    def index_card(self, data) -> bool:
        return self.db.cards.insert_one(data)

    def index_format(self, data) -> bool:
        return self.db.formats.insert_one(data)

    def index_page(self, data) -> bool:
        return self.db.pages.insert_one(data)

    def index_set(self, data) -> bool:
        return self.db.sets.insert_one(data)

    def index_type(self, data) -> bool:
        return self.db.types.insert_one(data)

    def has_card(self, card_id: int) -> bool:
        return self.db.cards.find_one({'card_id': card_id})

    def has_page(self, page_id: int) -> bool:
        return self.db.pages.find_one({'page_id': page_id})
