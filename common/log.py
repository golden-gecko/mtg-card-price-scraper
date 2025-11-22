import logging.handlers
import sys


logger = None


def get_logger():
    global logger

    if not logger:
        formatter = logging.Formatter('[%(asctime)s] [%(filename)s] [%(lineno)d] [%(levelname)s] %(message)s')

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)

        logger = logging.getLogger(__name__)
        logger.addHandler(stdout_handler)
        logger.setLevel(logging.DEBUG)

    return logger


def log_call(function):
    def wrapper(*args, **kwargs):
        if len(args):
            message = '{}({})'.format(function.__name__, ' ,'.join([str(arg) for arg in args]))
        else:
            message = '{}()'.format(function.__name__)

        get_logger().debug(message)

        return function(*args, **kwargs)

    return wrapper
