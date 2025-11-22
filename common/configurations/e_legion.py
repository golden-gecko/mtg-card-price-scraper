from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = [
    {
        'name': 'e_legion',
        'stages': [
            {
                'name': 'init',
                'steps': [
                    {
                        'stage': 'main',
                        'urls': [
                            'https://e-legion.pl/pl/c/Magic-the-Gathering-Single/13'
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
                            '#category_13 .level_1 a'
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
                            '#box_mainproducts .paginator a'
                        ]
                    },
                    {
                        'stage': 'product',
                        'selectors': [
                            '#box_mainproducts .products .prodimage'
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
                            'price': '#box_productfull .main-price',
                            'quantity': '#box_productfull .availability .second'
                        }
                    }
                ]
            }
        ]
    }
]
