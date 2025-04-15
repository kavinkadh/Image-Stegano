from PIL import Image
import os
import hashlib
from Crypto.Cipher import AES
from cryptography.fernet import Fernet

class Lemma:

    @staticmethod
    def _validate_image_format(image_path: str):
        """Validates that the image is either .png or .bmp format."""
        if not image_path.lower().endswith(('.png', '.bmp')):
            raise ValueError("Unsupported image format. Please use .png or .bmp files.")

    @staticmethod
    def prepare_hide(input_image_path: str, input_file_path: str):
        """Prepares the image and file for hiding data."""
        Lemma._validate_image_format(input_image_path)
        try:
            image = Image.open(input_image_path)
            file = open(input_file_path, 'rb')
            return image, file
        except (FileNotFoundError, IOError) as e:
            raise IOError(f"Error opening file: {e}")

    @staticmethod
    def prepare_recover(steg_image_path: str, output_file_path: str):
        """Prepares the steganographed image and output file for recovering data."""
        Lemma._validate_image_format(steg_image_path)
        try:
            image = Image.open(steg_image_path)
            file = open(output_file_path, 'wb')
            return image, file
        except (FileNotFoundError, IOError) as e:
            raise IOError(f"Error opening file: {e}")

    @staticmethod
    def get_image_capacity(image_path: str, num_lsb: int) -> int:
        """Calculates the maximum number of bits that can be hidden in the image."""
        Lemma._validate_image_format(image_path)
        try:
            image = Image.open(image_path)
            width, height = image.size
            num_channels = len(image.getbands())
            return width * height * num_channels * num_lsb
        except (FileNotFoundError, IOError) as e:
            raise IOError(f"Error calculating image capacity: {e}")

    @staticmethod
    def encrypt_message(message: bytes, key: str, method: str = 'AES') -> bytes:
        """Encrypts the message using the specified encryption method."""
        try:
            if method == 'AES':
                # Validate AES key length
                if len(key) not in [16, 24, 32]:
                    raise ValueError("AES key must be 16, 24, or 32 characters long.")
                key_bytes = key.encode('utf-8')
                cipher = AES.new(key_bytes, AES.MODE_EAX)
                ciphertext, tag = cipher.encrypt_and_digest(message)
                return cipher.nonce + tag + ciphertext
            elif method == 'FERNET':
                key_bytes = key.encode('utf-8')
                cipher_suite = Fernet(key_bytes)
                return cipher_suite.encrypt(message)
            else:
                raise ValueError("Invalid encryption method. Use 'AES' or 'FERNET'.")
        except Exception as e:
            raise RuntimeError(f"Error during message encryption: {e}")

    @staticmethod
    def decrypt_message(encrypted_message: bytes, key: str, method: str = 'AES') -> bytes:
        """Decrypts the message using the specified encryption method."""
        try:
            if method == 'AES':
                # Validate AES key length
                if len(key) not in [16, 24, 32]:
                    raise ValueError("AES key must be 16, 24, or 32 characters long.")
                key_bytes = key.encode('utf-8')
                nonce = encrypted_message[:16]
                tag = encrypted_message[16:32]
                ciphertext = encrypted_message[32:]
                cipher = AES.new(key_bytes, AES.MODE_EAX, nonce=nonce)
                return cipher.decrypt_and_verify(ciphertext, tag)
            elif method == 'FERNET':
                key_bytes = key.encode('utf-8')
                cipher_suite = Fernet(key_bytes)
                return cipher_suite.decrypt(encrypted_message)
            else:
                raise ValueError("Invalid decryption method. Use 'AES' or 'FERNET'.")
        except Exception as e:
            raise RuntimeError(f"Error during message decryption: {e}")

    @staticmethod
    def get_filesize(path: str) -> int:
        """Returns the size of the file in bytes."""
        return os.path.getsize(path)

    @staticmethod
    def max_bits_to_hide(image: Image.Image, num_lsb: int, num_channels: int) -> int:
        """Calculates the maximum number of bits that can be hidden in the image."""
        width, height = image.size
        max_bits = width * height * num_channels * num_lsb
        return max_bits

    @staticmethod
    def bytes_in_max_file_size(image: Image.Image, num_lsb: int, num_channels: int) -> int:
        """Calculates the number of bytes needed to store the size of the file to be hidden."""
        max_bits = Lemma.max_bits_to_hide(image, num_lsb, num_channels)
        return max_bits // 8

# Example test execution:
if __name__ == "__main__":
    # Increase image size for more capacity
    test_image = Image.new('RGB', (128, 128), color='white')  # Creating a 128x128 pixel image
    test_image_path = 'test_image.png'
    test_image.save(test_image_path)

    # Reduce message size to ensure it fits
    message = b'Hello, this is a test message!'
    num_lsb = 2
    key = "securekey1234567"  # 16 characters long key

    # Encrypt the message
    encrypted_message = Lemma.encrypt_message(message, key, method='AES')
    print(f"Encrypted message: {encrypted_message}")

    # Calculate image capacity
    image_capacity = Lemma.get_image_capacity(test_image_path, num_lsb)
    print(f"Image Capacity (in bytes): {image_capacity}")





