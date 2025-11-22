class GathererException(Exception):
    pass


class GathererDuplicateException(GathererException):
    pass


class GathererProcessingException(GathererException):
    pass


class GathererSkipException(GathererException):
    pass
