import os

from pymongo import MongoClient


client = MongoClient('192.168.0.162')

for root, _, files in os.walk('/data'):
    for file in files:
        path = os.path.join(root, file)

        if not client.scraper.pages.find_one({'cache.path': path}):
            print('Cache {} has no database entry'.format(path))

for page in client.scraper.pages.find():
    path = page['cache']['path']

    if not os.path.exists(path):
        print('Cache file {} does not exist'.format(path))
