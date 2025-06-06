from dataclasses import dataclass


@dataclass
class ReservationStatusData:
    has_finished_ticket_processing: bool
    has_finished_payment_processing: bool
