from broker.broker import Broker
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from typing import Any, Callable


class Subscriber(Broker):
    def __init__(
        self,
        host: str = "localhost",
    ) -> None:
        super().__init__(
            host=host,
        )

    def subscribe(
        self,
        queue_name: str,
        callback: Callable[
            [
                BlockingChannel,
                Basic.Deliver,
                BasicProperties,
                Any,
            ],
            Any,
        ],
        auto_ack: bool = False,
        exclusive: bool = False,
    ) -> None:
        self._channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=auto_ack,
            exclusive=exclusive,
        )

        self._channel.start_consuming()
