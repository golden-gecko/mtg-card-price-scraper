import threading

from log import get_logger
from scrapers.default.cache import ScraperCache
from scrapers.default.client import ScraperClient
from scrapers.default.db import ScraperDb
from scrapers.default.queue import ScraperQueue


logger = get_logger()


def process_pages(name, configuration):
    logger.info('Thread %s starting...', name)

    scraper = ScraperClient(
        cache=ScraperCache(directory='/data'),
        db=ScraperDb(host='mongo', database='scraper'),
        queue=ScraperQueue(host='rabbit')
    )
    scraper.add_configuration(name, configuration)
    scraper.process()

    logger.info('Thread %s exiting...', name)


def main():
    logger.info('Service starting...')

    """
    http://www.starcitygames.com/
    https://www.mtggoldfish.com/
    https://www.mtgrom.pl/
    https://isa.pl/k413-Single-MTG.html
    https://www.olx.pl/
    https://allegro.pl/
    http://www.swistak.pl/
    https://www.ebay.pl/
    """

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
        },
        'cardstore': {
            'init': [
                {
                    'stage': 'main',
                    'url': 'https://cardstore.pl/12-mtg-single'
                }
            ],
            'main': [
                {
                    'stage': 'category',
                    'selector': '#subcategories .subcategory-image a'
                }
            ],
            'category': [
                {
                    'stage': 'subcategory',
                    'selector': '#subcategories .subcategory-image a'
                }
            ],
            'subcategory': [
                {
                    'stage': 'subcategory',
                    'selector': '.pagination a'
                },
                {
                    'stage': 'product',
                    'selector': '.product_img_link'
                }
            ],
            'product': [
                {
                    'attributes': {
                        'condition': '#product_condition .editable',
                        'name': '#center_column .pb-center-column h1',
                        'price': '#our_price_display',
                        'quantity': '#quantityAvailable'
                    }
                }
            ]
        },
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
        },
        'centrum_mtg': {
            'init': [
                {
                    'stage': 'main',
                    'url': 'https://www.centrum-mtg.com.pl/pl/c/SINGLE/14'
                },
                {
                    'stage': 'main_foil',
                    'url': 'https://www.centrum-mtg.com.pl/pl/c/FOIL/83'
                }
            ],
            'main': [
                {
                    'stage': 'category',
                    'selector': '#category_14 .level_2 a'
                }
            ],
            'main_foil': [
                {
                    'stage': 'category',
                    'selector': '#category_83 .level_2 a'
                }
            ],
            'category': [
                {
                    'stage': 'category',
                    'selector': '.paginator a'
                },
                {
                    'stage': 'product',
                    'selector': '.products .prodimage'
                }
            ],
            'product': [
                {
                    'attributes': {
                        'name': '#box_productfull h1.name',
                        'price': '#box_productfull .main-price',
                        'quantity': '#box_productfull .availability .second'
                    }
                }
            ]
        },
        'e_legion': {
            'init': [
                {
                    'stage': 'main',
                    'url': 'https://e-legion.pl/pl/c/Magic-the-Gathering-Single/13'
                }
            ],
            'main': [
                {
                    'stage': 'category',
                    'selector': '#category_13 .level_1 a'
                }
            ],
            'category': [
                {
                    'stage': 'category',
                    'selector': '.paginator a'
                },
                {
                    'stage': 'product',
                    'selector': '.products .prodimage'
                }
            ],
            'product': [
                {
                    'attributes': {
                        'name': '#box_productfull h1.name',
                        'price': '#box_productfull .main-price',
                        'quantity': '#box_productfull .availability .second'
                    }
                }
            ]
        },
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
        },
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
        },
        'gamesmasters': {
            'init': [
                {
                    'stage': 'category',
                    'url': 'http://gamesmasters.pl/t/magic-the-gathering/single?on_page=60'
                }
            ],
            'category':
            [
                {
                    'stage': 'category',
                    'selector': '.paginator-small a'
                },
                {
                    'stage': 'product',
                    'selector': '.page-content .pl-title'
                }
            ],
            'product':
            [
                {
                    'attributes': {
                        'name': '.product-show-container h2.pl-small-padd',
                        'price': '.product-show-container .product-widgets .button-infogray-32px span span span',
                        'quantity': '.product-show-container .grid-01col.fright .button-infogray-32px span span span'
                    }
                }
            ]
        },
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
        },
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
        },
        'planeswalker': {
            'init': [
                {
                    'stage': 'main',
                    'url': 'https://planeswalker.pl/19-karty-na-sztuki'
                }
            ],
            'main': [
                {
                    'stage': 'category',
                    'selector': '#subcategories .subcategory-name'
                }
            ],
            'category': [
                {
                    'stage': 'category',
                    'selector': '#pagination a'
                },
                {
                    'stage': 'product',
                    'selector': '#product-list-karty .product-name'
                }
            ],
            'product': [
                {
                    'attributes': {
                        'condition': '.primary_block .pb-center-column #product_reference label:contains(Stan karty ) + span',
                        'name': '.primary_block .pb-center-column h1',
                        'price': '#our_price_display',
                        'quantity': '#quantity_wanted_p .quantity_wanted_text'
                    }
                }
            ]
        },
        'strefamtg': {
            'init': [
                {
                    'stage': 'main',
                    'url': 'https://www.strefamtg.pl/pl/3-single-mtg'
                }
            ],
            'main': [
                {
                    'stage': 'category',
                    'selector': '#subcategories .subcategory-image .img'
                }
            ],
            'category': [
                {
                    'stage': 'category',
                    'selector': '#pagination .pagination a'
                },
                {
                    'stage': 'product',
                    'selector': '.product_list .product_img_link'
                }
            ],
            'product': [
                {
                    'attributes': {
                        'condition': '#product_condition .editable',
                        'name': '.primary_block .pb-center-column h1',
                        'price': '#our_price_display',
                        'quantity': '#quantityAvailable'
                    }
                }
            ]
        }
    }

    try:
        threads = []

        for name, configuration in configurations.items():
            x = threading.Thread(target=process_pages, args=(name, configuration))
            x.start()

            threads.append(x)

        for thread in threads:
            thread.join()
    except KeyboardInterrupt as e:
        logger.warning('Processing stopped: %s', e)
    except Exception as e:
        logger.critical('Scraper failed: %s', e)

    logger.info('Service exiting...')


if __name__ == '__main__':
    main()
