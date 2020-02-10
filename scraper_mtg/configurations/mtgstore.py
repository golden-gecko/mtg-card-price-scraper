from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = {
    'mtgstore': {
        'init': [
            {
                'stage': 'main',
                'url': 'http://www.mtgstore.pl/index.php'
            }
        ],
        'main': [
            {
                'stage': 'category',
                'selector': '.box_kont .boxLink'
            }
        ],
        'category': [
            {
                'stage': 'category',
                'selector': '.inContent .pageResults'
            },
            {
                'stage': 'product',
                'selector': '.ProductTile'
            }
        ],
        'product': [
            {
                'attributes': {
                    'name': '.ProductInfoTile',
                    'price': '#nowaCena',
                    'quantity': 'tr:nth-child(2) .ProductHead:nth-child(2)'
                }
            }
        ]
    }
}
