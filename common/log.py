import inspect
import logging.handlers
import sys


loggers = {}


def get_logger(name=None):
    global loggers

    if name not in loggers:
        # formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
        formatter = logging.Formatter('[%(asctime)s] [%(filename)s] [%(lineno)d] [%(levelname)s] %(message)s')

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)

        loggers[name] = logging.getLogger(name)
        loggers[name].addHandler(stdout_handler)
        loggers[name].setLevel(logging.DEBUG)

    return loggers[name]


def log_call(instance=None):
    logger = get_logger(__name__)

    if instance is None:
        logger.debug('%s()', inspect.stack()[1][3])
    else:
        logger.debug('%s.%s()', type(instance).__name__, inspect.stack()[1][3])
