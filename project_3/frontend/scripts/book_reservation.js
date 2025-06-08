function main() {
  window.document
    .querySelector("#book_reservation_button")
    .addEventListener("click", (event) => {
      event.preventDefault();

      const number_of_passengers = document.getElementById("passengers").value;
      const number_of_cabins = document.getElementById("cabins").value;

      sessionStorage.setItem("number_of_passengers", number_of_passengers);
      sessionStorage.setItem("number_of_cabins", number_of_cabins);

      fetch("http://127.0.0.1:5000/book_reservation", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          number_of_passengers: sessionStorage["number_of_passengers"],
          number_of_cabins: sessionStorage["number_of_cabins"],
          destiny: sessionStorage["destiny"],
          boarding_date: sessionStorage["boarding_date"],
          boarding_port: sessionStorage["boarding_port"],
          ship_name: sessionStorage["ship_name"],
          number_of_nights: sessionStorage["number_of_nights"],
          price_per_person: sessionStorage["price_per_person"],
        }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.status === "not_available") {
            main_ = window.document.querySelector("main");
            p = window.document.createElement("p");
            p.innerHTML =
              "Number of selected cabins is bigger than the number of available cabins";
            main_.appendChild(p);
          } else {
            sessionStorage.setItem("reservation_id", data.reservation_id);
            window.location.href = "../pages/payment.html";
          }
        });
    });
}

main();
