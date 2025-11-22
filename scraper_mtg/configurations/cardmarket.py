from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = {
    'cardmarket': {
        'init': [
            {
                'stage': 'category',
                'url': 'https://www.cardmarket.com/en/Magic/Products/Singles?idCategory=1&idExpansion=0&idRarity=0&sortBy=name_asc&perSite=20'
            }
        ],
        'category': [
            {
                'stage': 'category',
                'selector': '#pagination .has-content-centered .btn'
            },
            {
                'stage': 'product',
                'selector': '.table-body .row.no-gutters .col .row.no-gutters a'
            }
        ],
        'product': [
            {
                'attributes': {
                    'name': '.page-title-container h1'
                }
            }
        ]
    }
}
