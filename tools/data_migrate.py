import hashlib
import json
import os
import re
import shutil

from pymongo import MongoClient
from scrapers.default.queue import ScraperQueue


def migrate_001():
    client = MongoClient('192.168.0.162')

    for root, _, files in os.walk('/data/flamberg'):
        for file in files:
            cache_path = os.path.join(root, file)
            page = client.scraper.pages.find_one({'cache.path': cache_path})

            if page is None:
                continue

            print(cache_path)
            print(page)

            url = page['url']
            timestamp = page['cache']['timestamp']

            print(url)
            print(timestamp)

            url_hash = hashlib.sha256(url.encode()).hexdigest()
            timestamp_hash = hashlib.sha256(timestamp.encode()).hexdigest()

            print(url_hash)
            print(timestamp_hash)

            url_escaped = re.sub('[^0-9a-zA-Z]+', '_', url)
            timestamp_escaped = re.sub('[^0-9]+', '_', timestamp)

            print(url_escaped)
            print(timestamp_escaped)

            src = cache_path
            dst = os.path.join(os.path.dirname(root), '{}_new'.format(os.path.basename(root)), os.path.basename(cache_path), timestamp_escaped)

            print(src)
            print(dst)

            if not os.path.exists(os.path.dirname(dst)):
                os.makedirs(os.path.dirname(dst))

            shutil.copy(src, dst)

            query = {'_id': page['_id']}
            new_values = {'$set': {'cache.path_new': dst}}

            client.scraper.pages.update_one(query, new_values)


def migrate_002():
    client = MongoClient('192.168.0.162')

    for page in client.scraper.pages.find():
        print(page)

        if 'path_new' not in page['cache']:
            continue

        query = {'_id': page['_id']}
        new_values = {'$set': {'cache.path': page['cache']['path_new']}}
        delete_values = {'$unset': {'cache.path_new': 1}}

        client.scraper.pages.update_one(query, new_values)
        client.scraper.pages.update_one(query, delete_values)


def migrate_003():
    client = MongoClient('192.168.0.162')

    for page in client.scraper.pages.find():
        print(page)

        query = {'_id': page['_id']}
        new_values = {'$set': {'cache.path': page['cache']['path'].replace('_new', '')}}

        client.scraper.pages.update_one(query, new_values)


def migrate_004():
    client = MongoClient('192.168.0.162')

    for page in client.scraper.pages.find():
        print(page)

        if 'versions' in page:
            continue

        query = {
            '_id': page['_id']
        }

        new_values = {
            '$set': {
                'versions': [
                    {
                        'cache': page['cache']
                    }
                ]
            }
        }

        if 'attributes' in page:
            new_values['$set']['versions'][0]['attributes'] = page['attributes']

        client.scraper.pages.update_one(query, new_values)


def migrate_005():
    client = MongoClient('192.168.0.162')

    for page in client.scraper.pages.find():
        print(page)

        query = {'_id': page['_id']}
        delete_values = {'$unset': {'attributes': 1, 'cache': 1}}

        client.scraper.pages.update_one(query, delete_values)


def migrate_006():
    client = MongoClient('192.168.0.162')
    query = {
        'attributes': {
            '$exists': True
        }
    }

    for page in client.scraper.pages.find(query):
        print(page)

        query = {'_id': page['_id']}

        versions = page['versions']
        versions[0]['attributes'] = page['attributes']

        add_values = {
            '$set': {
                'versions': versions
            }
        }

        delete_values = {
            '$unset': {
                'attributes': 1
            }
        }

        print(versions)
        print(delete_values)

        client.scraper.pages.update_one(query, add_values)
        client.scraper.pages.update_one(query, delete_values)


def migrate_007():
    queue = ScraperQueue('192.168.0.162')
    queue.connect()
    
    value = {
        'stage': 'product',
        'url': 'https://futurex.pl/pl/p/MTG-Boostery-Core-Set-2020/46469'
    }
    
    queue.publish('scraper_futurex', json.dumps(value))


# migrate_007()
