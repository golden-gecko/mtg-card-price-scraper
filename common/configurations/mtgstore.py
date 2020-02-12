from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = [
    {
        'name': 'mtgstore',
        'stages': [
            {
                'name': 'init',
                'steps': [
                    {
                        'stage': 'main',
                        'urls': [
                            'http://www.mtgstore.pl/index.php'
                        ]
                    }
                ]
            },
            {
                'name': 'main',
                'expires': ExpirationTime.month,
                'steps': [
                    {
                        'stage': 'category',
                        'selectors': [
                            '.box_kont .boxLink'
                        ]
                    }
                ]
            },
            {
                'name': 'category',
                'expires': ExpirationTime.month,
                'steps': [
                    {
                        'stage': 'category',
                        'selectors': [
                            '.inContent .pageResults'
                        ]
                    },
                    {
                        'stage': 'product',
                        'selectors': [
                            '.ProductTile'
                        ]
                    }
                ]
            },
            {
                'name': 'product',
                'expires': ExpirationTime.month,
                'steps': [
                    {
                        'attributes': {
                            'name': '.ProductInfoTile',
                            'price': '#nowaCena',
                            'quantity': 'tr:nth-child(2) .ProductHead:nth-child(2)'
                        }
                    }
                ]
            }
        ]
    }
]
