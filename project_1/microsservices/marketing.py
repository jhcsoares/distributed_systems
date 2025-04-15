from broker.publisher import Publisher
from json import dumps, load
from pathlib import Path


class Marketing:
    def __init__(
        self,
    ) -> None:
        self.__publisher = Publisher(
            host="localhost",
        )

    def create_promotion(
        self,
        destiny: str,
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
            if destiny == itinerary["destiny"]:
                self.__publisher.create_exchange(
                    exchange_type="fanout",
                    exchange_name=f"promotion_{destiny}_exchange",
                )
                self.__publisher.publish(
                    routing_key="",
                    message=dumps(itinerary),
                    exchange_name=f"promotion_{destiny}_exchange",
                )
