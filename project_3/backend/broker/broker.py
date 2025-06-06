import pika


class Broker:
    def __init__(
        self,
        host: str,
    ) -> None:
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
            ),
        )

        self._channel = self._connection.channel()

    def bind_queue_to_exchange(
        self,
        exchange_name: str,
        queue_name: str,
    ) -> None:
        self._channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
        )

    def create_queue(
        self,
        queue_name: str,
        exclusive: bool = False,
        durable: bool = False,
    ) -> None:
        self._channel.queue_declare(
            queue=queue_name,
            exclusive=exclusive,
            durable=durable,
        )

    def create_exchange(
        self,
        exchange_type: str,
        exchange_name: str = "",
    ) -> None:
        self._channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
        )

    def set_qos(
        self,
        qos: int = 1,
    ) -> None:
        self._channel.basic_qos(
            prefetch_count=qos,
        )
