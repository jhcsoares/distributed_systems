from broker.publisher import Publisher
from broker.subscriber import Subscriber
from cryptography.cryptography import Cryptography
from json import dumps, load, loads
from models.pending_reservation import PendingReservation, ReservationData
from pathlib import Path
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from threading import Thread
from typing import Dict
from uuid import uuid4


class Reservation:
    def __init__(
        self,
    ) -> None:
        self.__cryptography = Cryptography()

        self.__publisher = Publisher(
            host="localhost",
        )
        self.__publisher.create_queue(
            queue_name="created_reservations",
        )

        # {reservation_id: status}
        # True: payment finished
        # False: payment in process
        self.__payment_status_dict: Dict[str, bool] = {}

        self.__approved_payments_thread = Thread(
            target=self.__approved_payments_function,
            daemon=True,
        )

        self.__generated_tickets_thread = Thread(
            target=self.__generated_tickets_function,
            daemon=True,
        )

        self.__refused_payments_thread = Thread(
            target=self.__refused_payments_function,
            daemon=True,
        )

        self.__approved_payments_thread.start()

        self.__generated_tickets_thread.start()

        self.__refused_payments_thread.start()

    def __approved_payments_function(
        self,
    ) -> None:
        def approved_payments_callback(
            ch: BlockingChannel,
            method: Basic.Deliver,
            properties: BasicProperties,
            body: bytes,
        ) -> None:
            if not self.__cryptography.check_signature(
                message=body,
                public_key_name="approved_payments",
            ):
                print("Signature was not correctly checked!")

            else:
                reservation_id = body.decode()

                print(f"Reservation {reservation_id} has been paid successfully!")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        subscriber = Subscriber(
            host="localhost",
        )
        subscriber.create_exchange(
            exchange_type="fanout",
            exchange_name="approved_payments_exchange",
        )
        subscriber.create_queue(
            queue_name="approved_payments_1",
        )
        subscriber.bind_queue_to_exchange(
            exchange_name="approved_payments_exchange",
            queue_name="approved_payments_1",
        )
        subscriber.subscribe(
            queue_name="approved_payments_1",
            callback=approved_payments_callback,
        )

    def __generated_tickets_function(self) -> None:
        def generated_tickets_callback(
            ch: BlockingChannel,
            method: Basic.Deliver,
            properties: BasicProperties,
            body: bytes,
        ) -> None:

            ticket_data = loads(body)

            print(f"Here is your ticket: {ticket_data["ticket_id"]}")

            self.__payment_status_dict[ticket_data["reservation_id"]] = True

            ch.basic_ack(delivery_tag=method.delivery_tag)

        subscriber = Subscriber(
            host="localhost",
        )
        subscriber.create_queue(queue_name="generated_tickets")
        subscriber.subscribe(
            queue_name="generated_tickets",
            callback=generated_tickets_callback,
        )

    def __refused_payments_function(self) -> None:
        def refused_payments_callback(
            ch: BlockingChannel,
            method: Basic.Deliver,
            properties: BasicProperties,
            body: bytes,
        ) -> None:
            if not self.__cryptography.check_signature(
                message=body,
                public_key_name="refused_payments",
            ):
                print("Signature was not correctly checked!")

            else:
                reservation_id = body.decode()

                self.__payment_status_dict[reservation_id] = True

                print(f"Reservation {reservation_id} has not been paid successfully!")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        subscriber = Subscriber(
            host="localhost",
        )
        subscriber.create_queue(queue_name="refused_payments")
        subscriber.subscribe(
            queue_name="refused_payments",
            callback=refused_payments_callback,
        )

    def create_reservation(
        self,
        ship_name: str,
        boarding_date: str,
        number_of_passengers: int,
        number_of_cabins: int,
    ) -> None:
        itineraries_file = (
            Path(__file__).resolve().parent.parent / "data" / "itineraries.json"
        )

        with open(itineraries_file, "r") as f:
            itineraries = load(f)

        for itinerary in itineraries:
            if (
                ship_name == itinerary["ship_name"]
                and boarding_date == itinerary["boarding_date"]
            ):
                reservation_id = str(uuid4())

                self.__publisher.publish(
                    routing_key="created_reservations",
                    message=dumps(
                        PendingReservation(
                            reservation_id=reservation_id,
                            reservation_data=ReservationData(
                                boarding_date=boarding_date,
                                number_of_passengers=number_of_passengers,
                                number_of_cabins=number_of_cabins,
                            )._asdict(),
                        )._asdict()
                    ),
                )

                print(f"Created reservation id: {reservation_id}")

                self.__payment_status_dict.update(
                    {
                        reservation_id: False,
                    },
                )

                return

        print("No itineraries found!")

    def get_payment_status_by_reservation_id(
        self,
        reservation_id: str,
    ) -> bool:
        return self.__payment_status_dict.get(reservation_id)

    def list_itineraries(
        self,
        destiny: str,
        boarding_date: str,
        boarding_port: str,
    ) -> None:
        itineraries_file = (
            Path(__file__).resolve().parent.parent / "data" / "itineraries.json"
        )

        with open(
            itineraries_file,
            "r",
        ) as f:
            itineraries = load(f)

        for itinerary in itineraries:
            if (
                destiny == itinerary["destiny"]
                and boarding_date == itinerary["boarding_date"]
                and boarding_port == itinerary["boarding_port"]
            ):
                print(itinerary)
