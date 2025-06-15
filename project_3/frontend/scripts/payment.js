function main() {
  const payment_link_button = window.document.querySelector(
    "#payment_link_button"
  );

  payment_link_button.innerHTML = sessionStorage["reservation_id"];

  payment_link_button.addEventListener("click", (event) => {
    event.preventDefault();

    fetch("http://127.0.0.1:5000/make_payment", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        currency: "BRL",
        value:
          Number(sessionStorage["price_per_person"]) *
          Number(sessionStorage["number_of_passengers"]),
        reservation_id: sessionStorage["reservation_id"],
        number_of_cabins: sessionStorage["number_of_cabins"],
        ship_name: sessionStorage["ship_name"],
        boarding_date: sessionStorage["boarding_date"],
        boarding_port: sessionStorage["boarding_port"],
        destiny: sessionStorage["destiny"],
        client_id: sessionStorage["client_id"],
      }),
    }).catch((error) => {
      console.error("Payment error:", error);
    });
  });

  const source = new EventSource("http://127.0.0.1:5000/stream");

  source.onerror = function (err) {
    console.error("SSE Error:", err);
  };

  source.addEventListener(sessionStorage["reservation_id"], function (event) {
    const payment_status_section =
      window.document.querySelector(".payment_status");

    const response = JSON.parse(event.data);

    if (response.status === "approved") {
      payment_status_section.innerHTML = "Payment approved";
    } else {
      payment_status_section.innerHTML = "Payment reproved";
    }

    const home_section = window.document.createElement("section");
    home_section.classList.add("button-container");

    const home_button = window.document.createElement("button");

    home_button.innerHTML = "Home page";

    home_button.addEventListener("click", (event) => {
      event.preventDefault();

      window.location.href = "../pages/index.html";
    });

    home_section.appendChild(home_button);

    const main = window.document.querySelector("main");
    main.appendChild(home_section);
  });
}

main();
