function main() {
  if (!sessionStorage.getItem("client_id")) {
    client_id = crypto.randomUUID();
    sessionStorage.setItem("client_id", client_id);
  } else {
    client_id = sessionStorage.getItem("client_id");
  }

  window.document
    .querySelector("#view_itineraries_button")
    .addEventListener("click", () => {
      window.location.href = "../pages/view_itineraries.html";
    });

  window.document
    .querySelector("#cancel_reservation_button")
    .addEventListener("click", () => {
      window.location.href = "../pages/cancel_reservation.html";
    });

  window.document
    .querySelector("#promotions_subscribe_button")
    .addEventListener("click", () => {
      const source = new EventSource("http://127.0.0.1:5000/stream");

      fetch("http://127.0.0.1:5000/promotions_subscribe", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          client_id: client_id,
        }),
      });

      source.addEventListener(client_id, function (event) {
        let destiny_article = window.document.querySelector("#destiny_article");
        let boarding_date_article = window.document.querySelector(
          "#boarding_date_article"
        );
        let boarding_port_article = window.document.querySelector(
          "#boarding_port_article"
        );

        const itinerary = JSON.parse(event.data);

        destiny_article.innerHTML = itinerary.destiny;
        boarding_date_article.innerHTML = itinerary.boarding_date;
        boarding_port_article.innerHTML = itinerary.boarding_port;
      });
    });

  window.document
    .querySelector("#promotions_unsubscribe_button")
    .addEventListener("click", () => {
      let destiny_article = window.document.querySelector("#destiny_article");
      let boarding_date_article = window.document.querySelector(
        "#boarding_date_article"
      );
      let boarding_port_article = window.document.querySelector(
        "#boarding_port_article"
      );

      destiny_article.innerHTML = "";
      boarding_date_article.innerHTML = "";
      boarding_port_article.innerHTML = "";
      fetch("http://127.0.0.1:5000/promotions_unsubscribe", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          client_id: client_id,
        }),
      });
    });
}

main();
