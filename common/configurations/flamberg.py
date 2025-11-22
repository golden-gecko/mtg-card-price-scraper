from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = [
    {
        'name': 'flamberg',
        'stages': [
            {
                'name': 'init',
                'steps': [
                    {
                        'stage': 'main',
                        'urls': [
                            'http://flamberg.com.pl/'
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
                            '.contentContainer .row:nth-child(1) a'
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
                            '.pagination a'
                        ]
                    },
                    {
                        'stage': 'product',
                        'selectors': [
                            '#productListing td:first-child a'
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
                            'name': 'h1 a span',
                            'price': 'h1.pull-right span',
                            'quantity': '.list-unstyled.col-md-5 li:nth-child(4)'
                        }
                    }
                ]
            }
        ]
    }
]
