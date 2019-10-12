import pika

from log import get_logger


class RabbitClient:
    def __init__(self, host):
        self.connection_parameters = pika.ConnectionParameters(host)
        self.basic_properties = pika.BasicProperties(delivery_mode=2)

        self.connection = None

        self.logger = get_logger(__name__)

    def connect(self):
        self.connection = pika.BlockingConnection(parameters=self.connection_parameters)

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def create_channel(self):
        return self.connection.channel()

    def send(self, channel, queue_name, value) -> bool:
        channel.basic_publish(exchange='', routing_key=queue_name, body=value, properties=self.basic_properties)

        return True
