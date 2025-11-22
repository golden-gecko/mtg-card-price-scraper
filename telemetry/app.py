import psutil
import tcp_latency

from elasticsearch import Elasticsearch

import config

from log import get_logger
from utils import get_timestamp, wait


if __name__ == '__main__':
    logger = get_logger()
    logger.info('Processing starting...')

    telemetry = Elasticsearch([{'host': config.ELASTIC_HOST, 'port': config.ELASTIC_PORT}])

    while True:
        try:
            logger.info('Gathering data...')

            data = {
                'cpu': psutil.cpu_percent(),
                'memory': psutil.virtual_memory()._asdict()['percent'],
                'network_latency': tcp_latency.measure_latency('google.pl')[0],
                'timestamp': get_timestamp()
            }

            for x in psutil.sensors_temperatures()['coretemp']:
                data['core_temp_{}'.format(x.label.replace('Core ', ''))] = x.current

            telemetry.index(index='telemetry', body=data)

            wait(60.0)
        except KeyError as e:
            logger.warning('Processing stopped: %s', e)
