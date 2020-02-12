from bs4 import BeautifulSoup

from log import get_logger
from utils import ExpirationTime


logger = get_logger()

configurations = [
    {
        'name': 'gatherer',
        'stages': [
            {
                'name': 'init',
                'steps': [
                    {
                        'stage': 'page',
                        'urls': [
                            'https://gatherer.wizards.com/Pages/Search/Default.aspx?sort=cn+&page=0&name=%20[]'
                        ]
                    }
                ]
            },
            {
                'name': 'page',
                'expires': ExpirationTime.month,
                'steps': [
                    {
                        'stage': 'page',
                        'selectors': [
                            '#ctl00_ctl00_ctl00_MainContent_SubContent_topPagingControlsContainer a'
                        ]
                    },
                    {
                        'stage': 'card',
                        'selectors': [
                            '.cardItemTable .cardTitle a'
                        ]
                    }
                ]
            },
            {
                'name': 'card',
                'expires': ExpirationTime.month,
                'steps': [
                    {
                        'stage': 'card',
                        'selectors': [
                            '#ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_otherSetsValue a'
                        ]
                    },
                    {
                        'attributes': {
                            'name': '#ctl00_ctl00_ctl00_MainContent_SubContent_SubContentHeader_subtitleDisplay'
                        }
                    }
                ]
            }
        ]
    }
]
