from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = [
    {
        'name': 'cardstore',
        'stages': [
            {
                'name': 'init',
                'steps': [
                    {
                        'stage': 'main',
                        'urls': [
                            'https://cardstore.pl/12-mtg-single'
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
                            '#subcategories .subcategory-image a'
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
                            '#subcategories .subcategory-image a'
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
                            '.product_img_link'
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
                            'condition': '#product_condition .editable',
                            'name': '#center_column .pb-center-column h1',
                            'price': '#our_price_display',
                            'quantity': '#quantityAvailable'
                        }
                    }
                ]
            }
        ]
    }
]
