from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = [
    {
        'name': 'gamesmasters',
        'stages': [
            {
                'name': 'init',
                'steps': [
                    {
                        'stage': 'category',
                        'urls': [
                            'http://gamesmasters.pl/t/magic-the-gathering/single?on_page=60'
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
                            '.paginator-small a'
                        ]
                    },
                    {
                        'stage': 'product',
                        'selectors': [
                            '.page-content .pl-title'
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
                            'name': '.product-show-container h2.pl-small-padd',
                            'price': '.product-show-container .product-widgets .button-infogray-32px span span span',
                            'quantity': '.product-show-container .grid-01col.fright .button-infogray-32px span span span'
                        }
                    }
                ]
            }
        ]
    }
]
