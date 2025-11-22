from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = {
    'channelfireball': {
        'init': [
            {
                'stage': 'category',
                'url': 'https://store.channelfireball.com/catalog/magic_singles/8'
            }
        ],
        'category': [
            {
                'stage': 'category',
                'selector': '.parent-category a'
            },
            {
                'stage': 'category',
                'selector': '.page-tools-container a'
            },
            {
                'stage': 'product',
                'selector': '.products-container .product .meta a'
            }
        ],
        'product': [
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
}
