from typing import List, NamedTuple


class ItinerariesModel(NamedTuple):
    destiny: str
    boarding_date: str
    boarding_port: str
    destination_port: str
    ship_name: str
    visiting_places: List[str]
    number_of_nights: int
    price_per_person: float
