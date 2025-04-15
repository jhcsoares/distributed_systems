from broker.subscriber import Subscriber
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from threading import Thread
from uuid import uuid4


class Client:
    def __init__(
        self,
    ) -> None:
        pass

    def __promotion_function(
        self,
        destiny: str,
    ) -> None:
        def promotion_callback(
            ch: BlockingChannel,
            method: Basic.Deliver,
            properties: BasicProperties,
            body: bytes,
        ) -> None:

            print(f"Promotions: {body.decode()}")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        subscriber = Subscriber(
            host="localhost",
        )
        subscriber.create_exchange(
            exchange_type="fanout",
            exchange_name=f"promotion_{destiny}_exchange",
        )

        queue_name = str(uuid4())

        subscriber.create_queue(
            queue_name=queue_name,
        )
        subscriber.bind_queue_to_exchange(
            exchange_name=f"promotion_{destiny}_exchange",
            queue_name=queue_name,
        )
        subscriber.subscribe(
            queue_name=queue_name,
            callback=promotion_callback,
        )

    def execute(
        self,
    ) -> None:
        is_running = True
        while is_running:
            destiny = str(
                input("Type the destiny you want to receive promotions (0 to exit): ")
            )

            if destiny == "0":
                is_running = False

            else:
                promotion_thread = Thread(
                    target=self.__promotion_function,
                    args=(destiny,),
                    daemon=True,
                )
                promotion_thread.start()


if __name__ == "__main__":
    client = Client()
    client.execute()
