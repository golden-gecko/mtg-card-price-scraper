from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = [
    {
        'name': 'strefamtg',
        'stages': [
            {
                'name': 'init',
                'steps': [
                    {
                        'stage': 'main',
                        'urls': [
                            'https://www.strefamtg.pl/pl/3-single-mtg'
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
                            '#subcategories .subcategory-image .img'
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
                            '#pagination .pagination a'
                        ]
                    },
                    {
                        'stage': 'product',
                        'selectors': [
                            '.product_list .product_img_link'
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
                            'name': '.primary_block .pb-center-column h1',
                            'price': '#our_price_display',
                            'quantity': '#quantityAvailable'
                        }
                    }
                ]
            }
        ]
    }
]
