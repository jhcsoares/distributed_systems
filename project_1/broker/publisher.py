from broker.broker import Broker
from typing import Any

import pika


class Publisher(Broker):
    def __init__(
        self,
        host: str = "localhost",
    ) -> None:
        super().__init__(
            host=host,
        )

    def publish(
        self,
        routing_key: str,
        message: Any,
        exchange_name: str = "",
        is_persistent: bool = False,
    ) -> None:
        if is_persistent:
            properties = pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent,
            )

        else:
            properties = None

        self._channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=message,
            properties=properties,
        )

    def __del__(
        self,
    ) -> None:
        self._connection.close()
