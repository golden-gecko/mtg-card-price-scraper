from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = {
    'flamberg': {
        'init': [
            {
                'stage': 'main',
                'url': 'http://flamberg.com.pl/'
            }
        ],
        'main': [
            {
                'stage': 'category',
                'selector': '.contentContainer .row:nth-child(1) a'
            }
        ],
        'category': [
            {
                'stage': 'category',
                'selector': '.pagination a'
            },
            {
                'stage': 'product',
                'selector': '#productListing td:first-child a'
            }
        ],
        'product': [
            {
                'attributes': {
                    'name': 'h1 a span',
                    'price': 'h1.pull-right span',
                    'quantity': '.list-unstyled.col-md-5 li:nth-child(4)'
                }
            }
        ]
    }
}
