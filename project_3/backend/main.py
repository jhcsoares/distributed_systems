from flask import Flask, request
from flask_cors import CORS
from flask_sse import sse
from microsservices.marketing import Marketing
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
    url_prefix="/promotions_channel",
)

marketing = Marketing()
is_promotion_publishing = False
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
    request_data = request.get_json()
    client_id = request_data["client_id"]

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
    request_data = request.get_json()
    client_id = request_data["client_id"]

    is_client_subscribed_in_promotion.update(
        {
            client_id: False,
        },
    )

    return ""


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
    )
