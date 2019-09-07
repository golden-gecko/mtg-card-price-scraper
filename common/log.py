import inspect
import logging.handlers
import sys


logger = None


def get_logger(name=None):
    global logger

    if logger is None:
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)5s] %(message)s')

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)

        logger = logging.getLogger(name)
        logger.addHandler(stdout_handler)
        logger.setLevel(logging.DEBUG)

    return logger


def log_call(instance=None):
    if instance is None:
        get_logger().debug('%s()', inspect.stack()[1][3])
    else:
        get_logger().debug('%s.%s()', type(instance).__name__, inspect.stack()[1][3])
