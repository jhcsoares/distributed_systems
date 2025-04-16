from broker.publisher import Publisher
from broker.subscriber import Subscriber
from json import dumps, load
from pathlib import Path
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from time import sleep
from threading import Thread
from uuid import uuid4


class Marketing:
    def __init__(
        self,
    ) -> None:
        self.__publisher = Publisher(
            host="localhost",
        )

        self.__promotion_thread = Thread(
            target=self.__create_promotion,
            daemon=True,
        )
        self.__promotion_thread.start()

    def __create_promotion(
        self,
    ) -> None:
        itineraries_file = (
            Path(__file__).resolve().parent.parent / "data" / "itineraries.json"
        )

        with open(
            itineraries_file,
            "r",
        ) as f:
            itineraries = load(f)

        while True:
            for itinerary in itineraries:
                destiny = itinerary["destiny"]

                self.__publisher.create_exchange(
                    exchange_type="fanout",
                    exchange_name=f"promotion_{destiny}_exchange",
                )
                self.__publisher.publish(
                    routing_key="",
                    message=dumps(itinerary),
                    exchange_name=f"promotion_{destiny}_exchange",
                )

                sleep(15)

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

    def promotion_subscribe(
        self,
        destiny: str,
    ) -> None:
        promotion_thread = Thread(
            target=self.__promotion_function,
            args=(destiny,),
            daemon=True,
        )
        promotion_thread.start()
