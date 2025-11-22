from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = {
    'gamesmasters': {
        'init': [
            {
                'stage': 'category',
                'url': 'http://gamesmasters.pl/t/magic-the-gathering/single?on_page=60'
            }
        ],
        'category': [
            {
                'stage': 'category',
                'selector': '.paginator-small a'
            },
            {
                'stage': 'product',
                'selector': '.page-content .pl-title'
            }
        ],
        'product': [
            {
                'attributes': {
                    'name': '.product-show-container h2.pl-small-padd',
                    'price': '.product-show-container .product-widgets .button-infogray-32px span span span',
                    'quantity': '.product-show-container .grid-01col.fright .button-infogray-32px span span span'
                }
            }
        ]
    }
}
