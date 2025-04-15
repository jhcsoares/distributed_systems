from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from pathlib import Path


class Cryptography:
    def __init__(
        self,
    ) -> None:
        pass

    def check_signature(
        self,
        message: bytes,
        public_key_name: str,
    ) -> bool:
        public_key_path = (
            Path(__file__).resolve().parent.parent
            / "data"
            / f"{public_key_name}_public_key.der"
        )

        with open(public_key_path, "rb") as f:
            public_key = RSA.import_key(f.read())

        signature_path = (
            Path(__file__).resolve().parent.parent
            / "data"
            / f"{public_key_name}_signature.sig"
        )

        with open(signature_path, "rb") as f:
            signature = f.read()

        h = SHA256.new(message)

        try:
            pkcs1_15.new(public_key).verify(h, signature)
            return True

        except (ValueError, TypeError):
            return False

    def generate_keys(
        self,
        key_name: str,
    ) -> None:
        key = RSA.generate(2048)

        public_key_path = (
            Path(__file__).resolve().parent.parent
            / "data"
            / f"{key_name}_public_key.der"
        )

        with open(public_key_path, "wb") as f:
            f.write(key.public_key().export_key(format="DER"))

        private_key_path = (
            Path(__file__).resolve().parent.parent
            / "data"
            / f"{key_name}_private_key.der"
        )

        with open(private_key_path, "wb") as f:
            f.write(key.export_key(format="DER"))

    def sign_message(
        self,
        message: bytes,
        private_key_name: str,
    ) -> None:
        private_key_path = (
            Path(__file__).resolve().parent.parent
            / "data"
            / f"{private_key_name}_private_key.der"
        )

        with open(private_key_path, "rb") as f:
            private_key = RSA.import_key(f.read())

        h = SHA256.new(message)

        signature = pkcs1_15.new(private_key).sign(h)

        signature_path = (
            Path(__file__).resolve().parent.parent
            / "data"
            / f"{private_key_name}_signature.sig"
        )

        with open(signature_path, "wb") as f:
            f.write(signature)
