from broker.publisher import Publisher
from broker.subscriber import Subscriber
from json import dumps
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from threading import Thread
from uuid import uuid4


class Ticket:
    def __init__(
        self,
    ) -> None:
        self.__publisher = Publisher(
            host="localhost",
        )
        self.__publisher.create_queue(
            queue_name="generated_tickets",
        )

        self.__approved_payments_thread = Thread(
            target=self.__approved_payments_function,
            daemon=True,
        )
        self.__approved_payments_thread.start()

    def __approved_payments_function(
        self,
    ) -> None:
        def approved_payments_callback(
            ch: BlockingChannel,
            method: Basic.Deliver,
            properties: BasicProperties,
            body: bytes,
        ) -> None:
            ticket_id = str(uuid4())

            self.__publisher.publish(
                routing_key="generated_tickets",
                message=dumps(
                    {
                        "reservation_id": body.decode(),
                        "ticket_id": ticket_id,
                    }
                ),
            )

            ch.basic_ack(delivery_tag=method.delivery_tag)

        subscriber = Subscriber(
            host="localhost",
        )
        subscriber.create_exchange(
            exchange_type="fanout",
            exchange_name="approved_payments_exchange",
        )
        subscriber.create_queue(
            queue_name="approved_payments_2",
        )
        subscriber.bind_queue_to_exchange(
            exchange_name="approved_payments_exchange",
            queue_name="approved_payments_2",
        )
        subscriber.subscribe(
            queue_name="approved_payments_2",
            callback=approved_payments_callback,
        )
