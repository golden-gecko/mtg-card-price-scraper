from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = [
    {
        'name': 'planeswalker',
        'stages': [
            {
                'name': 'init',
                'steps': [
                    {
                        'stage': 'main',
                        'urls': [
                            'https://planeswalker.pl/19-karty-na-sztuki'
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
                            '#subcategories .subcategory-name'
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
                            '#pagination a'
                        ]
                    },
                    {
                        'stage': 'product',
                        'selectors': [
                            '#product-list-karty .product-name'
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
                            'condition': '.primary_block .pb-center-column #product_reference label:contains(Stan karty ) + span',
                            'name': '.primary_block .pb-center-column h1',
                            'price': '#our_price_display',
                            'quantity': '#quantity_wanted_p .quantity_wanted_text'
                        }
                    }
                ]
            }
        ]
    }
]
