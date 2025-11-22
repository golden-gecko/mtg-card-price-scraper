from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = [
    {
        'name': 'morigal',
        'stages': [
            {
                'name': 'init',
                'steps': [
                    {
                        'stage': 'main',
                        'urls': [
                            'http://morigal.pl/mtg-karty-na-sztuki-c-1/'
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
                            '.categories a.link'
                        ]
                    }
                ]
            },
            {
                'name': 'category',
                'expires': ExpirationTime.month,
                'steps': [
                    {
                        'stage': 'subcategory',
                        'selectors': [
                            '.categories a.link'
                        ]
                    }
                ]
            },
            {
                'name': 'subcategory',
                'expires': ExpirationTime.month,
                'steps': [
                    {
                        'stage': 'subcategory',
                        'selectors': [
                            '.pagination a'
                        ]
                    },
                    {
                        'stage': 'product',
                        'selectors': [
                            '.products .product-column .link'
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
                            'name': '#box-product .title',
                            'price': '#box-product .price',
                            'quantity': '#box-product .stock-available'
                        }
                    }
                ]
            }
        ]
    }
]
