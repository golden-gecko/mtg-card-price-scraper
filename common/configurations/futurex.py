from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = [
    {
        'name': 'futurex',
        'stages': [
            {
                'name': 'init',
                'steps': [
                    {
                        'stage': 'main',
                        'urls': [
                            'https://futurex.pl/pl/c/Magic-the-Gathering-MTG-karty/27'
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
                            '#category_27 .level_1 li a'
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
                            '.paginator a'
                        ]
                    },
                    {
                        'stage': 'product',
                        'selectors': [
                            '.product a'
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
                            'name': '#box_productfull h1.name',
                            'price': '#box_productfull .price em',
                            'quantity': '#box_productfull dd.availability'
                        }
                    }
                ]
            }
        ]
    }
]
