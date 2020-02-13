import psutil

from prometheus_client import Gauge, start_http_server

from log import get_logger
from utils import get_timestamp, wait


if __name__ == '__main__':
    logger = get_logger()
    logger.info('Processing starting...')

    cpu_usage = Gauge('cpu_usage', '')
    memory_usage = Gauge('memory_usage', '')

    start_http_server(8000)

    while True:
        try:
            logger.info('Gathering data...')

            cpu_usage.set(psutil.cpu_percent())
            memory_usage.set(psutil.virtual_memory()._asdict()['percent'])

            """
            for x in psutil.sensors_temperatures()['coretemp']:
                data['core_temp_{}'.format(x.label.replace('Core ', ''))] = x.current
            """

            wait(1.0)
        except KeyError as e:
            logger.warning('Processing stopped: %s', e)
