import logging.handlers
import sys

import config


logger = None


def get_logger():
    global logger

    if not logger:
        formatter = logging.Formatter('[%(asctime)s] [%(filename)s] [%(lineno)d] [%(levelname)s] %(message)s')

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)

        logger = logging.getLogger(__name__)
        logger.addHandler(stdout_handler)
        logger.setLevel(config.LOG_LEVEL)

    return logger


def log_call(function):
    def wrapper(*args, **kwargs):
        args_str = ', '.join([str(arg) for arg in args])
        kwargs_str = ', '.join([str(kwarg) for kwarg in kwargs.values()])

        logger.debug('{}({}, {})'.format(function.__name__, args_str, kwargs_str))

        return_value = function(*args, **kwargs)

        logger.debug('{}({}, {}): {}'.format(function.__name__, args_str, kwargs_str, return_value))

        return return_value

    return wrapper
