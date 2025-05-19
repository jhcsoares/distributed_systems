from math import ceil
from os import makedirs, path, rename
from Pyro5.api import expose, locate_ns, Proxy
from Pyro5.core import URI
from Pyro5.errors import CommunicationError, ConnectionClosedError
from Pyro5.server import Daemon
from Pyro5.nameserver import NameServer
from random import randint
from shutil import copy2, rmtree
from time import sleep
from threading import Event, Thread
from typing import Dict, List
from uuid import uuid4


@expose
class Peer(
    object,
):
    heartbeat_timeout_event = Event()
    election_timeout_event = Event()

    daemon = Daemon()

    # election timeout in seconds
    election_timeout = (
        randint(
            a=500,
            b=1500,
        )
        / 1000
    )

    # heartbeat timeout in s
    heartbeat_timeout = 1 / 1000

    current_epoch = 0

    is_peer_leader = False

    files_list: List[str] = []

    # file_name: List[peers]
    file_peers_map: Dict[str, List[URI]] = {}

    # epoch:True
    voted_elections_dict: Dict[int, bool] = {}

    def __init__(
        self,
    ):
        self.__request_loop_thread = Thread(
            target=self.__request_loop,
            daemon=True,
        )

        self.__election_timeout_thread = Thread(
            target=self.__election_timeout_function,
            daemon=True,
        )

        self.__heartbeat_timeout_thread = Thread(
            target=self.__heartbeat_timeout_function,
            daemon=True,
        )

    def __request_loop(
        self,
    ) -> None:
        Peer.daemon.requestLoop()

    def __election_timeout_function(
        self,
    ) -> None:
        while True:
            Peer.election_timeout_event.clear()

            if not Peer.election_timeout_event.wait(
                timeout=Peer.election_timeout,
            ):
                self.__start_election()

    def __heartbeat_timeout_function(
        self,
    ) -> None:
        while True:
            if Peer.heartbeat_timeout_event.wait():
                self.__send_heartbeat()
                sleep(
                    Peer.heartbeat_timeout,
                )

    def find_tracker(
        self,
    ) -> bool:
        nameserver: NameServer = locate_ns()

        if len(nameserver.list(prefix="tracker_epoch_")) >= 1:
            return True

        return False

    def get_tracker_files(
        self,
    ) -> List[str]:
        result = []

        for file, peers_list in Peer.file_peers_map.items():
            if peers_list:
                result.append(file)

        return result

    def __list_files_in_network(
        self,
    ) -> List[str]:
        nameserver: NameServer = locate_ns()

        object_dict: Dict[str, str] = nameserver.list(prefix="tracker_epoch_")

        tracker_uri = list(object_dict.values())[0]

        tracker: Peer = Proxy(
            uri=tracker_uri,
        )

        return tracker.get_tracker_files()

    def __list_peers_with_the_file(
        self,
        file_name: str,
    ) -> List[str]:
        nameserver: NameServer = locate_ns()

        object_dict: Dict[str, str] = nameserver.list(prefix="tracker_epoch_")

        tracker_uri = list(object_dict.values())[0]

        tracker: Peer = Proxy(
            uri=tracker_uri,
        )

        return tracker.get_tracker_file_peers_map(
            file_name=file_name,
        )

    def __start_election(
        self,
    ) -> None:
        nameserver: NameServer = locate_ns()

        objects_dict: Dict[str, str] = nameserver.list()

        # it's own vote
        votes = 1

        Peer.voted_elections_dict.update(
            {
                Peer.current_epoch + 1: True,
            },
        )

        # loop for voting
        for object_name, object_uri in objects_dict.items():
            if object_name != "Pyro.NameServer" and object_name != Peer.peer_id:
                try:
                    peer: Peer = Proxy(
                        uri=object_uri,
                    )

                    if peer.ask_peer_for_voting(election_epoch=Peer.current_epoch):
                        votes += 1

                except CommunicationError:
                    pass

                except ConnectionClosedError:
                    pass

        # removing name server from count
        if (
            votes
            >= ceil(
                (len(objects_dict) - 1) / 2,
            )
            and not self.find_tracker()
        ):
            print("I'm the new tracker")

            # remove peer id from nameserver to insert a new id as tracker
            nameserver.remove(
                name=Peer.peer_id,
            )

            old_peer_id = Peer.peer_id

            Peer.current_epoch += 1

            Peer.peer_id = f"tracker_epoch_{Peer.current_epoch}"

            rename(str(old_peer_id), Peer.peer_id)

            nameserver.register(
                name=Peer.peer_id,
                uri=Peer.peer_uri,
            )

            self.__register_files_in_tracker()

            Peer.is_peer_leader = True

            Peer.heartbeat_timeout_event.set()

        # loop for reseting election timeout
        for object_name, object_uri in objects_dict.items():
            if object_name != "Pyro.NameServer" and object_name != Peer.peer_id:
                try:
                    peer: Peer = Proxy(
                        uri=object_uri,
                    )

                    peer.reset_election_timeout()

                except CommunicationError:
                    pass

                except ConnectionClosedError:
                    pass

    def __send_heartbeat(
        self,
    ) -> None:
        nameserver: NameServer = locate_ns()

        objects_dict: Dict[str, str] = nameserver.list()

        for object_name, object_uri in objects_dict.items():
            if object_name != "Pyro.NameServer" and object_name != Peer.peer_id:
                try:
                    peer: Peer = Proxy(
                        uri=object_uri,
                    )

                    peer.receive_heartbeat(epoch=Peer.current_epoch)

                except CommunicationError:
                    pass

                except ConnectionClosedError:
                    pass

    def __register_files_in_tracker(
        self,
    ) -> None:
        nameserver: NameServer = locate_ns()

        object_dict: Dict[str, str] = nameserver.list(
            prefix="tracker_epoch_",
        )

        tracker_uri = list(object_dict.values())[0]

        tracker: Peer = Proxy(
            uri=tracker_uri,
        )

        tracker.receive_files(
            peer_id=Peer.peer_id,
            files_list=Peer.files_list,
        )

    def __download_file(
        self,
        file_name: str,
        peer_id: str,
    ) -> bool:
        nameserver: NameServer = locate_ns()

        object_dict: Dict[str, str] = nameserver.list(
            prefix=peer_id,
        )

        if not object_dict:
            return False

        peer: Peer = Proxy(
            uri=object_dict.get(peer_id),
        )

        peer.transmit_file(
            file_name=file_name,
            destination=Peer.peer_id,
        )

        Peer.files_list.append(
            file_name,
        )

        return True

    def transmit_file(
        self,
        file_name: str,
        destination: str,
    ) -> None:

        source_file = str(Peer.peer_id) + "/" + file_name

        destination_folder = destination

        makedirs(
            name=destination_folder,
            exist_ok=True,
        )

        destination_path = path.join(
            destination_folder,
            path.basename(source_file),
        )

        copy2(
            source_file,
            destination_path,
        )

    def __save_files(
        self,
    ) -> None:
        for file in Peer.files_list:

            source_file = "files/" + file

            destination_folder = str(Peer.peer_id)

            makedirs(
                name=destination_folder,
                exist_ok=True,
            )

            destination_path = path.join(
                destination_folder,
                path.basename(source_file),
            )

            copy2(
                source_file,
                destination_path,
            )

    def execute(
        self,
    ) -> None:
        self.__request_loop_thread.start()

        nameserver: NameServer = locate_ns()

        Peer.peer_uri = Peer.daemon.register(
            Peer,
        )

        Peer.peer_id = uuid4()

        nameserver.register(
            name=Peer.peer_id,
            uri=Peer.peer_uri,
        )

        continue_appending_files = True
        while continue_appending_files:
            file = str(input("Register file in this peer (0 to exit): "))

            if file != "0":
                Peer.files_list.append(file)

            else:
                continue_appending_files = False

        self.__save_files()

        if not self.find_tracker():
            self.__start_election()

        self.__register_files_in_tracker()

        self.__heartbeat_timeout_thread.start()

        self.__election_timeout_thread.start()

        is_peer_running = True
        while is_peer_running:
            print("1: List files in network")
            print("2: Download a file")
            print("3: Exit")

            option = str(input("Type an option: "))

            if option == "1":
                print("Available peers: ")
                print(self.__list_files_in_network())

            elif option == "2":
                file_name = str(input("Type file name: "))

                if file_name not in self.__list_files_in_network():
                    print("File does not exist")

                else:
                    print(
                        self.__list_peers_with_the_file(
                            file_name=file_name,
                        )
                    )

                    peer_id = str(
                        input("Select the peer where you want to download the file: ")
                    )

                    if self.__download_file(
                        file_name=file_name,
                        peer_id=peer_id,
                    ):
                        print("File downloaded")

                    else:
                        print("This peer does not have this file")

            elif option == "3":
                is_peer_running = False

    def ask_peer_for_voting(
        self,
        election_epoch: int,
    ) -> bool:
        if election_epoch < Peer.current_epoch and not Peer.voted_elections_dict.get(
            election_epoch,
        ):
            return False

        Peer.voted_elections_dict.update(
            {
                election_epoch: True,
            },
        )

        return True

    def reset_election_timeout(
        self,
    ) -> None:
        Peer.election_timeout_event.set()

    def receive_heartbeat(
        self,
        epoch: int,
    ) -> None:
        if not Peer.is_peer_leader:
            if Peer.current_epoch != epoch:
                Peer.__register_files_in_tracker(
                    self,
                )
                Peer.current_epoch = epoch
                Peer.election_timeout_event.set()

        # it means there is a draw in the election
        else:
            print("Draw in the election, I'm getting out")

            Peer.is_peer_leader = False

            Peer.heartbeat_timeout_event.clear()

            nameserver: NameServer = locate_ns()

            nameserver.remove(
                name=Peer.peer_id,
            )

            old_peer_id = Peer.peer_id

            Peer.peer_id = uuid4()

            rename(old_peer_id, str(Peer.peer_id))

            nameserver.register(
                name=Peer.peer_id,
                uri=Peer.peer_uri,
            )

    def receive_files(
        self,
        peer_id: str,
        files_list: List[str],
    ) -> None:
        for file in files_list:
            file_peers_list: List[str] = Peer.file_peers_map.get(
                file,
            )

            if file_peers_list:
                file_peers_list.append(peer_id)

            else:
                Peer.file_peers_map.update(
                    {
                        file: [
                            peer_id,
                        ],
                    },
                )

    def remove_files(
        self,
        peer_id: str,
        files_list: List[str],
    ) -> None:
        for file in files_list:
            file_peers_list: List[str] = Peer.file_peers_map.get(
                file,
            )

            if file_peers_list:
                file_peers_list.remove(peer_id)

    def __remove_files(
        self,
    ) -> None:
        nameserver: NameServer = locate_ns()

        object_dict: Dict[str, str] = nameserver.list(
            prefix="tracker_epoch_",
        )

        tracker_uri = list(object_dict.values())[0]

        tracker: Peer = Proxy(
            uri=tracker_uri,
        )

        tracker.remove_files(
            peer_id=Peer.peer_id,
            files_list=Peer.files_list,
        )

        rmtree(str(Peer.peer_id))

    def get_tracker_file_peers_map(
        self,
        file_name: str,
    ) -> Dict[str, List[URI]]:
        return Peer.file_peers_map.get(
            file_name,
        )

    def kill_peer(
        self,
    ) -> None:
        self.__remove_files()

        nameserver: NameServer = locate_ns()

        nameserver.remove(name=Peer.peer_id)


if __name__ == "__main__":
    peer = Peer()

    try:
        peer.execute()
        peer.kill_peer()

    except KeyboardInterrupt:
        peer.kill_peer()
        print("Peer killed")
