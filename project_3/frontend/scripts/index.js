function main() {
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
}

main();
