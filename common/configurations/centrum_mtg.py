from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = [
    {
        'name': 'centrum_mtg',
        'stages': [
            {
                'name': 'init',
                'steps': [
                    {
                        'stage': 'main',
                        'urls': [
                            'https://www.centrum-mtg.com.pl/pl/c/SINGLE/14'
                        ]
                    },
                    {
                        'stage': 'main_foil',
                        'urls': [
                            'https://www.centrum-mtg.com.pl/pl/c/FOIL/83'
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
                            '#category_14 .level_2 a'
                        ]
                    }
                ]
            },
            {
                'name': 'main_foil',
                'expires': ExpirationTime.month,
                'steps': [
                    {
                        'stage': 'category',
                        'selectors': [
                            '#category_83 .level_2 a'
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
