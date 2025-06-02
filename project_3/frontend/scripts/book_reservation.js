function main() {
  window.document
    .querySelector("#book_reservation_button")
    .addEventListener("click", (event) => {
      event.preventDefault();
      window.location.href = "../pages/payment.html";
    });
}

main();
