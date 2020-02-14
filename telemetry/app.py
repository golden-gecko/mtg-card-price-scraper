import psutil

from prometheus_client import Gauge, start_http_server

from log import get_logger
from utils import wait


if __name__ == '__main__':
    logger = get_logger()
    logger.info('Processing starting...')

    memory_usage = Gauge('memory_usage', '')

    cpu_load = []
    cpu_temperature = []
    cpu_usage = []

    for i, _ in enumerate(psutil.getloadavg()):
        cpu_load.append(Gauge('cpu_load_{}'.format(i), ''))

    for i, _ in enumerate(psutil.sensors_temperatures()['coretemp']):
        cpu_temperature.append(Gauge('cpu_temperatue_{}'.format(i), ''))

    for i, _ in enumerate(psutil.cpu_percent(percpu=True)):
        cpu_usage.append(Gauge('cpu_usage_{}'.format(i), ''))

    start_http_server(8000)

    while True:
        try:
            memory_usage.set(psutil.virtual_memory().percent)

            for i, load in enumerate(psutil.getloadavg()):
                cpu_load[i].set(load)

            for i, temperature in enumerate(psutil.sensors_temperatures()['coretemp']):
                cpu_temperature[i].set(temperature.current)

            for i, usage in enumerate(psutil.cpu_percent(percpu=True)):
                cpu_usage[i].set(usage)

            wait(10.0)
        except KeyError as e:
            logger.warning('Processing stopped: %s', e)
