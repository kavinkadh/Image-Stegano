import cv2
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os
from Steganography.Sierra import Sierra
from Steganography.Bravo import Bravo


class CryptoStegoManager:
    @staticmethod
    def embed_message(carrier_path: str, input_path: str, output_path: str, num_lsb: int = 2, key: str = "securekey", encryption_method: str = "AES"):
        """
        Embeds a message or file from the input_path into the carrier image.
        :param carrier_path: Path to the carrier image.
        :param input_path: Path to the text file or message to embed.
        :param output_path: Path to save the stego image.
        :param num_lsb: Number of LSBs to use for embedding.
        :param key: Encryption key for securing the message.
        :param encryption_method: Encryption method to use ("AES" or "Fernet").
        """
        try:
            # Open the carrier image
            carrier = Image.open(carrier_path)
            if carrier.format not in ["PNG", "BMP"]:
                raise ValueError("Only lossless image formats like PNG and BMP are supported.")

            # Modify detection sensitivity to avoid false positives in Sierra Module
            if Sierra.is_lsb_steganography(carrier_path, num_lsb):
                print("Warning: Carrier image might contain existing LSB data, but proceeding with embedding due to modified sensitivity.")

            # Read input file (text or binary)
            with open(input_path, 'rb') as file:
                payload = file.read()

            # Compute hash of the payload
            payload_hash = Bravo.compute_hash(payload)

            # Append hash to the payload
            payload_with_hash = payload_hash.encode() + payload

            # Encrypt the payload with hash
            encrypted_payload = Bravo.encrypt_message(payload_with_hash, key, method=encryption_method)

            # Embed the encrypted payload into the carrier image
            stego_image = Bravo.lsb_interleave_image(carrier, encrypted_payload, num_lsb)

            # Save the stego image to the output path
            stego_image.save(output_path)
            print(f"Stego image saved successfully at: {output_path}")

        except Exception as e:
            raise RuntimeError(f"Error during message embedding: {e}")

    @staticmethod
    def extract_message(stego_path: str, output_path: str, num_lsb: int = 2, key: str = "securekey", encryption_method: str = "AES"):
        """
        Extracts an embedded message or file from the stego image.
        :param stego_path: Path to the stego image containing the hidden message.
        :param output_path: Path to save the extracted message or file.
        :param num_lsb: Number of LSBs used for embedding.
        :param key: Encryption key for decrypting the message.
        :param encryption_method: Decryption method to use ("AES" or "Fernet").
        """
        try:
            # Open the stego image
            stego_image = Image.open(stego_path)
            if stego_image.format not in ["PNG", "BMP"]:
                raise ValueError("Only lossless image formats like PNG and BMP are supported.")

            # Validate if the image contains LSB steganography using Sierra Module
            if not Sierra.is_lsb_steganography(stego_path, num_lsb):
                print("Warning: No LSB steganographic data detected in the stego image, but attempting extraction due to modified sensitivity.")

            # Calculate the number of bits to extract based on the image capacity
            image_capacity = Bravo.max_bits_to_hide(stego_image, num_lsb)

            # Extract the encrypted payload from the stego image
            extracted_encrypted_payload = Bravo.lsb_deinterleave_image(stego_image, image_capacity, num_lsb)

            # Decrypt the extracted payload
            extracted_payload_with_hash = Bravo.decrypt_message(extracted_encrypted_payload, key, method=encryption_method)

            # Extract the hash and the actual payload
            extracted_hash = extracted_payload_with_hash[:64].decode()  # SHA-256 hash is 64 characters
            extracted_payload = extracted_payload_with_hash[64:]

            # Verify the hash
            recalculated_hash = Bravo.compute_hash(extracted_payload)
            if extracted_hash != recalculated_hash:
                raise ValueError("Hash mismatch! The extracted message may be corrupted.")

            # Save the extracted payload to the output path
            with open(output_path, 'wb') as output_file:
                output_file.write(extracted_payload)
            print(f"Extracted message saved successfully at: {output_path}")

        except Exception as e:
            raise RuntimeError(f"Error during message extraction: {e}")

    @staticmethod
    def user_choice(operation: str, carrier_path: str, input_path: str = None, output_path: str = None, num_lsb: int = 2, key: str = "securekey", encryption_method: str = "AES"):
        """
        Allows the user to choose between embedding or extracting a message.
        :param operation: "embed" for embedding a message, "extract" for extracting a message.
        :param carrier_path: Path to the carrier or stego image.
        :param input_path: Path to the text file or message to embed (required for embedding).
        :param output_path: Path to save the output (required for both embedding and extraction).
        :param num_lsb: Number of LSBs to use for embedding/extracting.
        :param key: Encryption key for securing or decrypting the message.
        :param encryption_method: Encryption method to use ("AES" or "Fernet").
        """
        if operation.lower() == "embed":
            if not input_path or not output_path:
                raise ValueError("Input and output paths must be provided for embedding.")
            CryptoStegoManager.embed_message(carrier_path, input_path, output_path, num_lsb, key, encryption_method)
        elif operation.lower() == "extract":
            if not output_path:
                raise ValueError("Output path must be provided for extraction.")
            CryptoStegoManager.extract_message(carrier_path, output_path, num_lsb, key, encryption_method)
        else:
            raise ValueError("Invalid operation. Choose 'embed' or 'extract'.")

    @staticmethod
    def analyze_stego_image(stego_path: str):
        """
        Analyzes the stego image using various techniques from the Sierra Module.
        :param stego_path: Path to the stego image.
        """
        try:
            print("Performing LSB distribution analysis...")
            Sierra.analyze_lsb_distribution(stego_path, num_lsb=1)

            print("Performing RS analysis...")
            rs_ratio = Sierra.rs_analysis(stego_path)
            print(f"RS analysis ratio: {rs_ratio}")

            print("Performing spatial analysis...")
            Sierra.spatial_analysis(stego_path)
        except Exception as e:
            raise RuntimeError(f"Error during stego image analysis: {e}")

# Example usage
if __name__ == "__main__":
    # User choice example
    try:
        CryptoStegoManager.user_choice(
            operation="embed",  # Choose "embed" or "extract"
            carrier_path="carrier_image.png",
            input_path="message.txt",  # Required for embedding
            output_path="stego_image.png",  # Required for both embedding and extraction
            num_lsb=2,
            key="securekey",
            encryption_method="FERNET"  # Choose between "AES" or "FERNET"
        )

        # Example of extraction
        CryptoStegoManager.user_choice(
            operation="extract",
            carrier_path="stego_image.png",
            output_path="extracted_message.txt",
            num_lsb=2,
            key="securekey",
            encryption_method="FERNET"
        )

        # Example of stego image analysis
        CryptoStegoManager.analyze_stego_image("stego_image.png")

    except Exception as e:
        print(f"An error occurred: {e}")
