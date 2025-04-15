import random
import hashlib
from cryptography.fernet import Fernet
from Crypto.Cipher import AES


class Bravo:

    @staticmethod
    def validate_inputs(carrier: bytes, payload: bytes, num_lsb: int):
        """Validates input parameters for LSB interleaving and deinterleaving."""
        if not isinstance(carrier, (bytes, bytearray)):
            raise TypeError("Carrier must be a byte stream.")
        if not isinstance(payload, (bytes, bytearray)):
            raise TypeError("Payload must be a byte stream.")
        if num_lsb < 1 or num_lsb > 7:
            raise ValueError("num_lsb must be between 1 and 7.")
        if len(payload) * 8 > len(carrier) * num_lsb:
            raise ValueError("Payload is too large to be hidden in the carrier.")

    @staticmethod
    def lsb_interleave_bytes(carrier: bytes, payload: bytes, num_lsb: int, truncate: bool = False) -> bytes:
        """Embeds the payload into the least significant bits of the carrier byte stream."""
        Bravo.validate_inputs(carrier, payload, num_lsb)

        payload_bits = ''.join(f'{byte:08b}' for byte in payload)
        payload_len = len(payload_bits)
        carrier_bits = [f'{byte:08b}' for byte in carrier]

        payload_index = 0
        try:
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
                required_length = len(payload) * 8 // num_lsb
                interleaved_bytes = interleaved_bytes[:required_length]

            return interleaved_bytes
        except Exception as e:
            raise RuntimeError(f"Error during LSB interleaving: {e}")

    @staticmethod
    def lsb_deinterleave_bytes(carrier: bytes, num_bits: int, num_lsb: int) -> bytes:
        """Extracts the payload from the least significant bits of the carrier byte stream."""
        try:
            bits_extracted = []
            carrier_bits = [f'{byte:08b}' for byte in carrier]

            for i in range(len(carrier_bits)):
                carrier_byte = carrier_bits[i]
                for j in range(num_lsb):
                    if len(bits_extracted) < num_bits:
                        bits_extracted.append(carrier_byte[-1 - j])

            payload_bits = ''.join(bits_extracted[:num_bits])
            payload = bytes(int(payload_bits[i:i + 8], 2) for i in range(0, len(payload_bits), 8))

            return payload
        except Exception as e:
            raise RuntimeError(f"Error during LSB deinterleaving: {e}")

    @staticmethod
    def encrypt_payload(payload: bytes, key: str, method: str = 'AES') -> bytes:
        """Encrypts the payload using the specified encryption method."""
        try:
            if method == 'AES':
                # Validate AES key length
                if len(key) not in [16, 24, 32]:
                    raise ValueError("AES key must be 16, 24, or 32 characters long.")
                key_bytes = key.encode('utf-8')
                cipher = AES.new(key_bytes, AES.MODE_EAX)
                ciphertext, tag = cipher.encrypt_and_digest(payload)
                return cipher.nonce + tag + ciphertext
            elif method == 'FERNET':
                key_bytes = key.encode('utf-8')
                cipher_suite = Fernet(key_bytes)
                return cipher_suite.encrypt(payload)
            else:
                raise ValueError("Invalid encryption method. Use 'AES' or 'FERNET'.")
        except Exception as e:
            raise RuntimeError(f"Error during payload encryption: {e}")

    @staticmethod
    def decrypt_payload(encrypted_payload: bytes, key: str, method: str = 'AES') -> bytes:
        """Decrypts the payload using the specified encryption method."""
        try:
            if method == 'AES':
                # Validate AES key length
                if len(key) not in [16, 24, 32]:
                    raise ValueError("AES key must be 16, 24, or 32 characters long.")
                key_bytes = key.encode('utf-8')
                nonce = encrypted_payload[:16]
                tag = encrypted_payload[16:32]
                ciphertext = encrypted_payload[32:]
                cipher = AES.new(key_bytes, AES.MODE_EAX, nonce=nonce)
                return cipher.decrypt_and_verify(ciphertext, tag)
            elif method == 'FERNET':
                key_bytes = key.encode('utf-8')
                cipher_suite = Fernet(key_bytes)
                return cipher_suite.decrypt(encrypted_payload)
            else:
                raise ValueError("Invalid decryption method. Use 'AES' or 'FERNET'.")
        except Exception as e:
            raise RuntimeError(f"Error during payload decryption: {e}")

    @staticmethod
    def compute_hash(data: bytes) -> str:
        """Computes the SHA-256 hash of the given data."""
        try:
            return hashlib.sha256(data).hexdigest()
        except Exception as e:
            raise RuntimeError(f"Error computing hash: {e}")

    @staticmethod
    def test(carrier_len: int = 10 ** 3, payload_len: int = 10 ** 2, num_lsb: int = 2, method: str = 'AES') -> bool:
        """Validates the interleaving and deinterleaving process."""
        try:
            carrier = bytes(random.getrandbits(8) for _ in range(carrier_len))
            payload = bytes(random.getrandbits(8) for _ in range(payload_len))

            # Generate appropriate key for the selected encryption method
            if method == 'AES':
                # AES key must be 16, 24, or 32 characters
                key = "securekey1234567"  # Example 16-character key for AES
            elif method == 'FERNET':
                # Fernet requires a Base64-encoded key
                key = Fernet.generate_key().decode()
            else:
                raise ValueError("Invalid encryption method. Use 'AES' or 'FERNET'.")

            # Encrypt payload
            encrypted_payload = Bravo.encrypt_payload(payload, key, method=method)

            # Interleave encrypted payload
            interleaved = Bravo.lsb_interleave_bytes(carrier, encrypted_payload, num_lsb)

            # Deinterleave and decrypt payload
            extracted_encrypted_payload = Bravo.lsb_deinterleave_bytes(interleaved, len(encrypted_payload) * 8, num_lsb)
            extracted_payload = Bravo.decrypt_payload(extracted_encrypted_payload, key, method=method)

            # Verify integrity with hash
            original_hash = Bravo.compute_hash(payload)
            extracted_hash = Bravo.compute_hash(extracted_payload)

            return original_hash == extracted_hash
        except Exception as e:
            raise RuntimeError(f"Error during test execution: {e}")

# Example of running the test with AES encryption
test_result_aes = Bravo.test(method='AES')
print(f"Test result with AES: {test_result_aes}")

# Example of running the test with Fernet encryption
test_result_fernet = Bravo.test(method='FERNET')
print(f"Test result with Fernet: {test_result_fernet}")
