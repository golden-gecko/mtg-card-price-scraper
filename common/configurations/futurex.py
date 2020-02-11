from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = {
    'futurex': {
        'init': [
            {
                'stage': 'main',
                'url': 'https://futurex.pl/pl/c/Magic-the-Gathering-MTG-karty/27'
            }
        ],
        'main': [
            {
                'stage': 'category',
                'selector': '#category_27 .level_1 li a'
            }
        ],
        'category': [
            {
                'stage': 'category',
                'selector': '.paginator a'
            },
            {
                'stage': 'product',
                'selector': '.product a'
            }
        ],
        'product': [
            {
                'attributes': {
                    'name': '#box_productfull h1.name',
                    'price': '#box_productfull .price em',
                    'quantity': '#box_productfull dd.availability'
                }
            }
        ]
    }
}
