from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = {
    'morigal': {
        'init': [
            {
                'stage': 'main',
                'url': 'http://morigal.pl/mtg-karty-na-sztuki-c-1/'
            }
        ],
        'main': [
            {
                'stage': 'category',
                'selector': '.categories a.link'
            }
        ],
        'category': [
            {
                'stage': 'subcategory',
                'selector': '.categories a.link'
            }
        ],
        'subcategory': [
            {
                'stage': 'subcategory',
                'selector': '.pagination a'
            },
            {
                'stage': 'product',
                'selector': '.products .product-column .link'
            }
        ],
        'product': [
            {
                'attributes': {
                    'name': '#box-product .title',
                    'price': '#box-product .price',
                    'quantity': '#box-product .stock-available'
                }
            }
        ]
    }
}
