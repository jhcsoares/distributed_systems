from typing import NamedTuple


class ReservationData(NamedTuple):
    boarding_date: str
    number_of_passengers: int
    number_of_cabins: int


class PendingReservation(NamedTuple):
    reservation_id: str
    reservation_data: ReservationData
