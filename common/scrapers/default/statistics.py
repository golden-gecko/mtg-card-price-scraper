from prometheus_client import Counter, Gauge, start_http_server

from log import get_logger


class ScraperStatistics:
    def __init__(self):
        self.logger = get_logger()

        self.page_cache_age = Gauge('scraper_page_cache_age', '')
        self.page_download_total = Counter('scraper_page_download_total', '')
        self.page_download_time = Gauge('scraper_page_download_time', '')
        self.page_index_total = Counter('scraper_page_index_total', '')
        self.page_index_time = Gauge('scraper_page_index_time', '')

    def run(self):
        start_http_server(8000)
