from flask import Flask, request
from flask_cors import CORS
from requests import post
from typing import Dict


app = Flask(
    __name__,
)

CORS(
    app=app,
    origins="*",
)


@app.route(
    "/make_payment",
    methods=["POST"],
)
def make_payment() -> str:
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
        port=5001,
    )
