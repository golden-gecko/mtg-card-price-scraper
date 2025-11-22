class ScraperException(Exception):
    pass


class ScraperDuplicateException(ScraperException):
    pass


class ScraperProcessingException(ScraperException):
    pass


class ScraperSkipException(ScraperException):
    pass
