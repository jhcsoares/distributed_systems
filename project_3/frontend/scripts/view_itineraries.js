function main() {
  document.querySelector("form").addEventListener("submit", function (event) {
    event.preventDefault();

    const destiny = document.getElementById("destiny").value;
    const boarding_date = document.getElementById("boarding_date").value;
    const boarding_port = document.getElementById("boarding_port").value;

    fetch(
      `http://127.0.0.1:5000/itineraries?destiny=${destiny}&boarding_date=${boarding_date}&boarding_port=${boarding_port}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    )
      .then((res) => res.json())
      .then((data) => {
        let itinerary = null;

        const tbody = document.querySelector("tbody");
        tbody.innerHTML = "";

        for (itinerary of data) {
          const tr = document.createElement("tr");

          let td = null;

          td = document.createElement("td");
          td.innerHTML = itinerary["boarding_date"];
          tr.appendChild(td);

          td = document.createElement("td");
          td.innerHTML = itinerary["ship_name"];
          tr.appendChild(td);

          td = document.createElement("td");
          td.innerHTML = itinerary["boarding_port"];
          tr.appendChild(td);

          td = document.createElement("td");
          td.innerHTML = itinerary["visiting_places"];
          tr.appendChild(td);

          td = document.createElement("td");
          td.innerHTML = itinerary["number_of_nights"];
          tr.appendChild(td);

          td = document.createElement("td");
          td.innerHTML = itinerary["price_per_person"];
          tr.appendChild(td);

          td = document.createElement("td");
          td.innerHTML = itinerary["number_of_available_cabins"];
          tr.appendChild(td);

          td = document.createElement("td");

          button = document.createElement("button");
          button.textContent = "Book";
          button.addEventListener("click", () => {
            sessionStorage.setItem(
              (key = "destiny"),
              (value = itinerary["destiny"])
            );
            sessionStorage.setItem(
              (key = "boarding_date"),
              (value = itinerary["boarding_date"])
            );
            sessionStorage.setItem(
              (key = "boarding_port"),
              (value = itinerary["boarding_port"])
            );
            sessionStorage.setItem(
              (key = "ship_name"),
              (value = itinerary["ship_name"])
            );
            sessionStorage.setItem(
              (key = "number_of_nights"),
              (value = itinerary["number_of_nights"])
            );
            sessionStorage.setItem(
              (key = "price_per_person"),
              (value = itinerary["price_per_person"])
            );

            window.location.href = "../pages/book_reservation.html";
          });

          td.appendChild(button);
          tr.appendChild(td);

          tbody.appendChild((node = tr));
        }
      });
  });
}

main();
