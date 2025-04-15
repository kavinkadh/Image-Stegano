import os
from PIL import Image
from Bravo import Bravo
from Lemma import Lemma

class SecretMessage:

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

            # Read input file (text or binary)
            with open(input_path, 'rb') as file:
                payload = file.read()

            # Encrypt the payload
            encrypted_payload = Bravo.encrypt_message(payload, key, method=encryption_method)

            # Embed the encrypted payload into the carrier image
            stego_image = Bravo.lsb_interleave_image(carrier, encrypted_payload, num_lsb)

            # Save the stego image to the output path
            stego_image.save(output_path)
            print(f"Stego image saved successfully at: {output_path}")

        except Exception as e:
            raise RuntimeError(f"Error during message embedding: {e}")

# Example usage
if __name__ == "__main__":
    # Embed a message or file into an image
    carrier_image_path = "carrier_image.png"
    input_file_path = "message.txt"  # Path to text or file to embed
    output_stego_image_path = "stego_image.png"

    try:
        SecretMessage.embed_message(
            carrier_path=carrier_image_path,
            input_path=input_file_path,
            output_path=output_stego_image_path,
            num_lsb=2,
            key="securekey",
            encryption_method="FERNET"  # Choose between "AES" or "FERNET"
        )
    except Exception as e:
        print(f"An error occurred: {e}")
