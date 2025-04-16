from cryptography.cryptography import Cryptography
from microsservices.marketing import Marketing
from microsservices.payment import Payment
from microsservices.reservation import Reservation
from microsservices.ticket import Ticket


class Main:
    def __init__(
        self,
    ) -> None:
        self.__cryptography = Cryptography()

        self.__marketing = Marketing()

        self.__payment = Payment()

        self.__reservation = Reservation()

        self.__ticket = Ticket()

    def execute(
        self,
    ) -> None:
        self.__cryptography.generate_keys(
            key_name="approved_payments",
        )
        self.__cryptography.generate_keys(
            key_name="refused_payments",
        )
        self.__cryptography.generate_keys(
            key_name="created_reservations",
        )

        is_running = True
        while is_running:
            print("Option 1: List itineraries")
            print("Option 2: Make a reservation")
            print("Option 3: Make the payment")
            print("Option 4: Refuse the payment")
            print("Option 5: Subscribe in a promotion")
            print("Option 6: Exit")

            option = str(input("Type your option: "))

            if option == "1":
                destiny = str(input("Type your destiny: "))
                boarding_date = str(input("Type your boarding date: "))
                boarding_port = str(input("Type your boarding port: "))

                self.__reservation.list_itineraries(
                    destiny=destiny,
                    boarding_date=boarding_date,
                    boarding_port=boarding_port,
                )

            elif option == "2":
                ship_name = str(input("Type your ship name: "))
                boarding_date = str(input("Type your boarding date: "))
                number_of_passengers = int(input("Type the number of passengers: "))
                number_of_cabins = int(input("Type the number of cabins: "))

                self.__reservation.create_reservation(
                    ship_name=ship_name,
                    boarding_date=boarding_date,
                    number_of_passengers=number_of_passengers,
                    number_of_cabins=number_of_cabins,
                )

            elif option == "3":
                reservation_id = str(input("Reservation id: "))

                if self.__payment.make_payment(reservation_id=reservation_id):
                    while (
                        not self.__reservation.get_reservation_status_by_reservation_id(
                            reservation_id=reservation_id
                        )
                    ):
                        # busy waiting
                        pass

            elif option == "4":
                reservation_id = str(input("Reservation id: "))

                if self.__payment.refuse_payment(reservation_id=reservation_id):
                    while (
                        not self.__reservation.get_reservation_status_by_reservation_id(
                            reservation_id=reservation_id
                        )
                    ):
                        # busy waiting
                        pass

            elif option == "5":
                destiny = str(input("Type your destiny: "))

                self.__marketing.promotion_subscribe(
                    destiny=destiny,
                )

            elif option == "6":
                is_running = False

            # \n
            print()


if __name__ == "__main__":
    main = Main()
    main.execute()
