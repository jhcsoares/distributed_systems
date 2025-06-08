function main() {
  const client_id = sessionStorage.getItem("client_id");

  fetch(`http://127.0.0.1:5000/reservations?client_id=${client_id}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((res) => res.json())
    .then((data) => {
      console.log(data);
      let itinerary = null;

      const tbody = document.querySelector("tbody");
      tbody.innerHTML = "";

      for (itinerary of data) {
        const tr = document.createElement("tr");

        let td = null;

        td = document.createElement("td");
        td.innerHTML = itinerary["ticket_id"];
        tr.appendChild(td);

        td = document.createElement("td");
        td.innerHTML = itinerary["boarding_date"];
        tr.appendChild(td);

        td = document.createElement("td");
        td.innerHTML = itinerary["boarding_port"];
        tr.appendChild(td);

        td = document.createElement("td");
        td.innerHTML = itinerary["destiny"];
        tr.appendChild(td);

        td = document.createElement("td");

        button = document.createElement("button");
        button.textContent = "Cancel reservation";
        button.addEventListener("click", () => {
          tr.remove();

          fetch("http://127.0.0.1:5000/cancel_reservation", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              client_id: sessionStorage.getItem("client_id"),
              ticket_id: itinerary["ticket_id"],
            }),
          });
        });

        td.appendChild(button);
        tr.appendChild(td);

        tbody.appendChild((node = tr));
      }
    });
}

main();
