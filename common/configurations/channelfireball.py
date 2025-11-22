from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = [
    {
        'name': 'channelfireball',
        'stages': [
            {
                'name': 'init',
                'steps': [
                    {
                        'stage': 'category',
                        'urls': [
                            'https://store.channelfireball.com/catalog/magic_singles/8'
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
                            '.parent-category a',
                            '.page-tools-container a'
                        ]
                    },
                    {
                        'stage': 'product',
                        'selectors': [
                            '.products-container .product .meta a'
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
                            'condition': '.variant-main-info .variant-short-info',
                            'name': '.product-info .title',
                            'price': '.product-price-qty .price',
                            'quantity': '.variant-main-info .variant-short-info .qty-count'
                        }
                    }
                ]
            }
        ]
    }
]
