from broker.publisher import Publisher
from broker.subscriber import Subscriber
from json import dump, dumps, load, loads
from models.pending_reservation import PendingReservation, ReservationData
from pathlib import Path
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from threading import Thread
from typing import Dict


class Payment:
    def __init__(
        self,
    ) -> None:

        # {reservation_id: ReservationData}
        self.__pending_reservations_dict: Dict[str, ReservationData] = {}

        self.__publisher = Publisher(
            host="localhost",
        )
        self.__publisher.create_exchange(
            exchange_type="fanout",
            exchange_name="approved_payments_exchange",
        )
        self.__publisher.create_queue(
            queue_name="refused_payments",
        )

        self.__created_reservations_thread = Thread(
            target=self.__created_reservations_function,
            daemon=True,
        )

        self.__created_reservations_thread.start()

    def __created_reservations_function(self) -> None:
        def created_reservations_callback(
            ch: BlockingChannel,
            method: Basic.Deliver,
            properties: BasicProperties,
            body: bytes,
        ) -> None:
            pending_reservation = PendingReservation(**loads(body))

            self.__pending_reservations_dict.update(
                {
                    pending_reservation.reservation_id: pending_reservation.reservation_data
                }
            )

            ch.basic_ack(delivery_tag=method.delivery_tag)

        subscriber = Subscriber(
            host="localhost",
        )
        subscriber.create_queue(queue_name="created_reservations")
        subscriber.subscribe(
            queue_name="created_reservations",
            callback=created_reservations_callback,
        )

    def make_payment(
        self,
        client_id: str,
        boarding_port: str,
        boarding_date: str,
        destiny: str,
        reservation_id: str,
    ) -> bool:
        if self.__pending_reservations_dict.get(reservation_id):
            message = {
                "reservation_id": reservation_id,
                "client_id": client_id,
                "boarding_port": boarding_port,
                "boarding_date": boarding_date,
                "destiny": destiny,
            }

            self.__publisher.publish(
                routing_key="",
                message=dumps(message),
                exchange_name="approved_payments_exchange",
            )

            self.__pending_reservations_dict.pop(reservation_id)

            return True

        else:
            print("This reservation does not exist!")

            return False

    def __update_itineraries(
        self,
        ship_name: str,
        boarding_date: str,
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
                itinerary["number_of_available_cabins"] += number_of_cabins

                with open(itineraries_file, "w") as f:
                    dump(itineraries, f, indent=4)

                break

    def refuse_payment(
        self,
        reservation_id: str,
        ship_name: str,
        boarding_date: str,
        number_of_cabins: int,
    ) -> bool:
        if self.__pending_reservations_dict.get(reservation_id):

            Thread(
                target=self.__update_itineraries,
                args=(
                    ship_name,
                    boarding_date,
                    number_of_cabins,
                ),
            ).start()

            message = reservation_id

            self.__publisher.publish(
                routing_key="refused_payments",
                message=message,
            )

            self.__pending_reservations_dict.pop(reservation_id)

            return True

        else:
            print("This reservation does not exist!")

            return False
