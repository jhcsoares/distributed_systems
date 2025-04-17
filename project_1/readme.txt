This program was developed to run in Ubuntu 20.04.

Download Rabbitmq and start the server

(Optional reset)
sudo systemctl stop rabbitmq-server
sudo systemctl start rabbitmq-server

Download Python>=3.8. Once it is installed, inside the root directory, you must run:
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python3 main.py
