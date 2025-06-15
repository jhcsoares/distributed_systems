from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sse import sse
from microsservices.marketing import Marketing
from microsservices.payment import Payment
from microsservices.reservation import Reservation
from microsservices.ticket import Ticket
from requests import post
from threading import Thread
from time import sleep
from typing import Dict

app = Flask(
    __name__,
)

CORS(
    app=app,
    origins="*",
)

app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(
    blueprint=sse,
    url_prefix="/stream",
)

marketing = Marketing()
payment = Payment()
reservation = Reservation()
ticket = Ticket()

is_client_subscribed_in_promotion: Dict[str, bool] = {}


def publish_promotions(
    client_id: str,
) -> None:
    global marketing

    marketing.promotion_subscribe()

    while is_client_subscribed_in_promotion[client_id]:
        with app.app_context():
            sse.publish(
                data=marketing.current_promotion,
                type=client_id,
            )

        sleep(1)


@app.route(
    "/promotions_subscribe",
    methods=["POST"],
)
def promotion_subscribe() -> str:
    request_data: Dict[str, str] = request.get_json()

    client_id: str = request_data["client_id"]

    is_client_subscribed_in_promotion.update(
        {
            client_id: True,
        },
    )

    Thread(
        target=publish_promotions,
        args=(client_id,),
    ).start()

    return ""


@app.route(
    "/promotions_unsubscribe",
    methods=["POST"],
)
def promotion_unsubscribe() -> str:
    request_data: Dict[str, str] = request.get_json()

    client_id: str = request_data["client_id"]

    is_client_subscribed_in_promotion.update(
        {
            client_id: False,
        },
    )

    return ""


@app.route(
    "/itineraries",
    methods=["GET"],
)
def get_itineraries() -> str:
    global reservation

    date_obj = datetime.strptime(
        request.args["boarding_date"],
        "%Y-%m-%d",
    )
    boarding_date_formatted = date_obj.strftime(
        format="%m/%d/%Y",
    )

    itineraries = reservation.get_itineraries(
        destiny=request.args["destiny"],
        boarding_date=boarding_date_formatted,
        boarding_port=request.args["boarding_port"],
    )

    return (
        jsonify(
            itineraries,
        ),
        200,
    )


@app.route(
    "/book_reservation",
    methods=["POST"],
)
def book_reservation() -> str:
    global reservation

    request_data: Dict[str, str] = request.get_json()

    itineraries = reservation.get_itineraries(
        destiny=request_data["destiny"],
        boarding_date=request_data["boarding_date"],
        boarding_port=request_data["boarding_port"],
    )

    for itinerary in itineraries:
        if (
            itinerary["destiny"] == request_data["destiny"]
            and itinerary["boarding_date"] == request_data["boarding_date"]
            and itinerary["boarding_port"] == request_data["boarding_port"]
            and itinerary["ship_name"] == request_data["ship_name"]
            and str(itinerary["number_of_nights"]) == request_data["number_of_nights"]
            and str(itinerary["price_per_person"]) == request_data["price_per_person"]
        ):
            if (
                int(request_data["number_of_cabins"])
                > itinerary["number_of_available_cabins"]
            ):
                return (
                    jsonify(
                        {
                            "status": "not_available",
                        },
                    ),
                    200,
                )

            else:
                reservation_id = reservation.create_reservation(
                    ship_name=request_data["ship_name"],
                    boarding_date=request_data["boarding_date"],
                    number_of_passengers=int(
                        request_data["number_of_passengers"],
                    ),
                    number_of_cabins=int(
                        request_data["number_of_cabins"],
                    ),
                )

                return (
                    jsonify(
                        {
                            "status": "available",
                            "reservation_id": reservation_id,
                        },
                    ),
                    200,
                )


# webhook
@app.route(
    "/approve_payment",
    methods=["POST"],
)
def approve_payment() -> str:
    global reservation

    request_data: Dict[str, str] = request.get_json()

    # it waits for the queue publication
    while not reservation.get_reservations_by_client_id(
        client_id=request_data["client_id"]
    ):
        sleep(0.1)

    with app.app_context():
        sse.publish(
            data={
                "status": "approved",
            },
            type=request_data["reservation_id"],
        )

    return (
        jsonify(
            {
                "status": "approved",
            },
        ),
        200,
    )


# webhook
@app.route(
    "/refuse_payment",
    methods=["POST"],
)
def refuse_payment() -> str:
    global payment

    request_data: Dict[str, str] = request.get_json()

    with app.app_context():
        sse.publish(
            data={
                "status": "refused",
            },
            type=request_data["reservation_id"],
        )

    return (
        jsonify(
            {
                "status": "refused",
            },
        ),
        200,
    )


@app.route(
    "/reservations",
    methods=["GET"],
)
def get_reservations() -> str:
    global reservation

    result = reservation.get_reservations_by_client_id(
        client_id=request.args["client_id"]
    )

    return (
        jsonify(result),
        200,
    )


@app.route(
    "/cancel_reservation",
    methods=["POST"],
)
def cancel_reservation() -> str:
    global reservation

    request_data: Dict[str, str] = request.get_json()

    reservation.cancel_reservation(
        client_id=request_data["client_id"],
        ticket_id=request_data["ticket_id"],
    )

    return (
        jsonify(),
        200,
    )


# external payment service
@app.route(
    "/make_payment",
    methods=["POST"],
)
def make_payment() -> str:
    global payment

    request_data: Dict[str, str] = request.get_json()

    currency: str = request_data["currency"]
    value = int(request_data["value"])
    reservation_id: str = request_data["reservation_id"]
    number_of_cabins: str = request_data["number_of_cabins"]
    ship_name: str = request_data["ship_name"]
    boarding_date: str = request_data["boarding_date"]
    boarding_port: str = request_data["boarding_port"]
    destiny: str = request_data["destiny"]
    client_id: str = request_data["client_id"]

    if currency == "BRL" and value > 0 and value < 100000:
        payment.make_payment(
            client_id=client_id,
            reservation_id=reservation_id,
            destiny=destiny,
            boarding_date=boarding_date,
            boarding_port=boarding_port,
        )

        post(
            url="http://127.0.0.1:5000/approve_payment",
            json={
                "reservation_id": reservation_id,
                "client_id": client_id,
                "boarding_date": boarding_date,
                "boarding_port": boarding_port,
                "destiny": destiny,
            },
        )

    else:
        payment.refuse_payment(
            reservation_id=request_data["reservation_id"],
            ship_name=request_data["ship_name"],
            boarding_date=request_data["boarding_date"],
            number_of_cabins=int(request_data["number_of_cabins"]),
        )

        post(
            url="http://127.0.0.1:5000/refuse_payment",
            json={
                "reservation_id": reservation_id,
                "number_of_cabins": number_of_cabins,
                "ship_name": ship_name,
                "boarding_date": boarding_date,
            },
        )

    return ""


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
    )
