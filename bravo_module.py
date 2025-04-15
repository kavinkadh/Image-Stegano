import numpy as np
import random
import hashlib
from cryptography.fernet import Fernet


class Bravo:

    @staticmethod
    def validate_inputs(carrier: bytes, payload: bytes, num_lsb: int, byte_depth: int):
        """Validates input parameters for LSB interleaving and deinterleaving."""
        if not isinstance(carrier, (bytes, bytearray)):
            raise TypeError("Carrier must be a byte stream.")
        if not isinstance(payload, (bytes, bytearray)):
            raise TypeError("Payload must be a byte stream.")
        if num_lsb < 1 or num_lsb > 7:
            raise ValueError("num_lsb must be between 1 and 7.")
        if len(payload) * 8 > len(carrier) * num_lsb * byte_depth:
            raise ValueError("Payload is too large to be hidden in the carrier.")

    @staticmethod
    def lsb_interleave_bytes(carrier: bytes, payload: bytes, num_lsb: int, truncate: bool = False,
                             byte_depth: int = 1) -> bytes:
        """Embeds the payload into the least significant bits of the carrier byte stream."""
        Bravo.validate_inputs(carrier, payload, num_lsb, byte_depth)

        payload_bits = ''.join(f'{byte:08b}' for byte in payload)
        payload_len = len(payload_bits)
        carrier_bits = list(f'{byte:08b}' for byte in carrier)

        payload_index = 0
        for i in range(len(carrier_bits)):
            if payload_index >= payload_len:
                break

            carrier_byte = list(carrier_bits[i])
            for j in range(num_lsb):
                if payload_index < payload_len:
                    carrier_byte[-1 - j] = payload_bits[payload_index]
                    payload_index += 1
            carrier_bits[i] = ''.join(carrier_byte)

        interleaved_bytes = bytes(int(carrier_bits[i], 2) for i in range(len(carrier_bits)))

        if truncate:
            required_length = (len(payload) * 8 + num_lsb - 1) // num_lsb
            interleaved_bytes = interleaved_bytes[:required_length]

        return interleaved_bytes

    @staticmethod
    def lsb_deinterleave_bytes(carrier: bytes, num_bits: int, num_lsb: int, byte_depth: int = 1) -> bytes:
        """Extracts the payload from the least significant bits of the carrier byte stream."""
        if not isinstance(carrier, (bytes, bytearray)):
            raise TypeError("Carrier must be a byte stream.")

        bits_extracted = []

        for byte in carrier:
            carrier_bits = f'{byte:08b}'
            for j in range(num_lsb):
                bits_extracted.append(carrier_bits[-1 - j])

        payload_bits = ''.join(bits_extracted[:num_bits])
        payload = bytes(int(payload_bits[i:i + 8], 2) for i in range(0, len(payload_bits), 8))

        return payload
    @staticmethod
    def encrypt_payload(payload: bytes, key: bytes) -> bytes:
        """Encrypts the payload using Fernet symmetric encryption."""
        cipher_suite = Fernet(key)
        encrypted_payload = cipher_suite.encrypt(payload)
        return encrypted_payload

    @staticmethod
    def decrypt_payload(encrypted_payload: bytes, key: bytes) -> bytes:
        """Decrypts the payload using Fernet symmetric encryption."""
        cipher_suite = Fernet(key)
        decrypted_payload = cipher_suite.decrypt(encrypted_payload)
        return decrypted_payload

    @staticmethod
    def compute_hash(data: bytes) -> str:
        """Computes the SHA-256 hash of the given data."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def test(carrier_len: int = 10 ** 3, payload_len: int = 10 ** 2) -> bool:
        """Validates the interleaving and deinterleaving process."""
        carrier = bytes(random.getrandbits(8) for _ in range(carrier_len))
        payload = bytes(random.getrandbits(8) for _ in range(payload_len))

        num_lsb = 2

        # Encrypt payload
        key = Fernet.generate_key()
        encrypted_payload = Bravo.encrypt_payload(payload, key)

        # Interleave encrypted payload
        interleaved = Bravo.lsb_interleave_bytes(carrier, encrypted_payload, num_lsb)

        # Deinterleave and decrypt payload
        extracted_encrypted_payload = Bravo.lsb_deinterleave_bytes(interleaved, len(encrypted_payload) * 8, num_lsb)
        extracted_payload = Bravo.decrypt_payload(extracted_encrypted_payload, key)

        # Verify integrity with hash
        original_hash = Bravo.compute_hash(payload)
        extracted_hash = Bravo.compute_hash(extracted_payload)

        return original_hash == extracted_hash


# Run the test
test_result = Bravo.test()
test_result
