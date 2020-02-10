from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()


def mock_product_get_condition(soup: BeautifulSoup):
    selector = '.condition'

    logger.warning('Searching for attribute with selector "%s"', selector)

    value = soup.select_one(selector)

    logger.debug('value: %s', value)

    if not value:
        return ''

    logger.debug('value: %s', value)

    return value.text.replace('Condition ', '')


def mock_product_get_price(soup: BeautifulSoup):
    selector = '.price'

    logger.warning('Searching for attribute with selector "%s"', selector)

    value = soup.select_one(selector)

    logger.debug('value: %s', value)

    if not value:
        return ''

    logger.debug('value: %s', value)

    return value.text.replace(' USD', '')


configurations = [
    {
        'name': 'market',
        'stages': [
            {
                'name': 'init',
                'steps': [
                    {
                        'stage': 'main',
                        'urls': [
                            'http://10.10.0.20/'
                        ]
                    }
                ]
            },
            {
                'name': 'main',
                'expires': ExpirationTime.minute,
                'steps': [
                    {
                        'stage': 'category',
                        'selectors': [
                            '.category a'
                        ]
                    }
                ]
            },
            {
                'name': 'category',
                'expires': ExpirationTime.minute,
                'steps': [
                    {
                        'stage': 'product',
                        'selectors': [
                            '.product a'
                        ]
                    }
                ]
            },
            {
                'name': 'product',
                'expires': ExpirationTime.hour,
                'steps': [
                    {
                        'attributes': {
                            'name': '.name',
                            'price': mock_product_get_price,
                            'condition': mock_product_get_condition,
                            'quantity': '.quantity'
                        }
                    }
                ]
            }
        ]
    },
    {
        'name': 'shop',
        'stages': [
            {
                'name': 'init',
                'steps': [
                    {
                        'stage': 'main',
                        'urls': [
                            'http://10.10.0.20/'
                        ]
                    }
                ]
            },
            {
                'name': 'main',
                'expires': ExpirationTime.hour,
                'steps': [
                    {
                        'stage': 'category',
                        'selectors': [
                            '.category a'
                        ]
                    }
                ]
            },
            {
                'name': 'category',
                'expires': ExpirationTime.hour,
                'steps': [
                    {
                        'stage': 'product',
                        'selectors': [
                            '.product a'
                        ]
                    }
                ]
            },
            {
                'name': 'product',
                'expires': ExpirationTime.minute,
                'steps': [
                    {
                        'attributes': {
                            'name': '.name',
                            'price': mock_product_get_price,
                            'condition': mock_product_get_condition,
                            'quantity': '.quantity'
                        }
                    }
                ]
            }
        ]
    }
]
