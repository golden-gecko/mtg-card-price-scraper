import logging.handlers
import sys


loggers = {}


def get_logger(name=None):
    global loggers

    if name not in loggers:
        formatter = logging.Formatter('[%(asctime)s] [%(filename)s] [%(lineno)d] [%(levelname)s] %(message)s')

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)

        loggers[name] = logging.getLogger(name)
        loggers[name].addHandler(stdout_handler)
        loggers[name].setLevel(logging.DEBUG)

    return loggers[name]


def log_call(function):
    def wrapper(*args, **kwargs):
        if len(args):
            message = '{}({})'.format(function.__name__, ' ,'.join([str(arg) for arg in args]))
        else:
            message = '{}()'.format(function.__name__)

        get_logger().debug(message)

        return function(*args, **kwargs)

    return wrapper
