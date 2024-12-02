"""
Wrapper for pika
"""

import json
import logging
import os
from time import sleep

import pika

LOGGER = logging.getLogger(__name__)


class PikaWrapper:
    """
    Wrapper for pika (e.g., to handle exceptions)
    """

    def __init__(self, connection_name: str) -> None:
        """
        Init
        """
        self.connection = None
        self.channel = None
        self.connection_name = connection_name

        self.init()

    def init(self):
        """
        Open a connection and a channel
        """
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=os.environ["RABBITMQ_HOST"],
                port=int(os.environ.get("RABBITMQ_PORT", "5672")),
                credentials=pika.credentials.PlainCredentials(
                    username=os.environ["RABBITMQ_USER"],
                    password=os.environ["RABBITMQ_PASSWORD"],
                ),
                client_properties={
                    "connection_name": self.connection_name,
                },
            )
        )
        self.channel = self.connection.channel()
        LOGGER.info("Connection and channel open")

    def publish(self, routing_key, message: any) -> bool:
        """
        message should can be any JSON-serializable object
        """
        for _ in range(10):
            try:
                self.channel.basic_publish(
                    exchange="",
                    routing_key=routing_key,
                    body=json.dumps(message).encode(),
                    properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
                )
                LOGGER.debug("%s pushed to RabbitMQ queue", message)
                return True
            except Exception:
                LOGGER.exception("Fail to use channel: open a new connection with a new channel.")
                self.init()
            sleep(1)

        return False

    def close(self):
        """
        Close channel and connection
        """
        self.channel.close()
        self.connection.close()
