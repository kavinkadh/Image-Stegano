from PIL import Image
import os

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
        image = Image.open(input_image_path)
        file = open(input_file_path, 'rb')
        return image, file

    @staticmethod
    def prepare_recover(steg_image_path: str, output_file_path: str):
        """Prepares the steganographed image and output file for recovering data."""
        Lemma._validate_image_format(steg_image_path)
        image = Image.open(steg_image_path)
        file = open(output_file_path, 'wb')
        return image, file

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

    @staticmethod
    def hide_message_in_image(input_image: Image.Image, message: bytes, num_lsb: int, skip_storage_check: bool = False):
        """Hides the message in the image using the specified number of LSBs."""
        width, height = input_image.size
        pixels = list(input_image.getdata())
        num_channels = len(input_image.getbands())

        if not skip_storage_check:
            max_bits = Lemma.max_bits_to_hide(input_image, num_lsb, num_channels)
            if len(message) * 8 + 32 > max_bits:  # Including space for the length
                raise ValueError("The message is too large to hide in the image.")

        # Convert the message to bits and prepend the length of the message
        message_length = len(message)
        message_bits = f'{message_length:032b}'  # Store length in the first 32 bits
        message_bits += ''.join([format(byte, '08b') for byte in message])

        print("Message length (in bits):", len(message_bits))
        print("Message bits:", message_bits)

        bit_idx = 0
        new_pixels = []

        for pixel in pixels:
            new_pixel = list(pixel)  # Copy the original pixel values
            for i in range(num_channels):
                if bit_idx < len(message_bits):
                    bit_segment = message_bits[bit_idx:bit_idx + num_lsb]
                    lsb_value = int(bit_segment, 2)
                    print(f"Embedding bits {bit_segment} (value: {lsb_value}) into pixel[{i}] of {pixel[i]}")
                    new_pixel[i] = Lemma.set_lsbs(new_pixel[i], lsb_value, num_lsb)
                    bit_idx += num_lsb
            new_pixels.append(tuple(new_pixel))
            if bit_idx >= len(message_bits):
                break

        # Append the remaining unmodified pixels
        new_pixels.extend(pixels[len(new_pixels):])

        image_with_message = Image.new(input_image.mode, input_image.size)
        image_with_message.putdata(new_pixels)
        return image_with_message


    @staticmethod
    def hide_data(input_image_path: str, input_file_path: str, steg_image_path: str, num_lsb: int,
                  compression_level: int = 0, skip_storage_check: bool = False):
        """Hides data from a file within an image and saves it as a new image."""
        Lemma._validate_image_format(input_image_path)
        Lemma._validate_image_format(steg_image_path)
        image, file = Lemma.prepare_hide(input_image_path, input_file_path)
        message = file.read()
        file.close()

        hidden_image = Lemma.hide_message_in_image(image, message, num_lsb, skip_storage_check)

        # Save the steganographed image
        hidden_image.save(steg_image_path, format='PNG', compress_level=compression_level)


    @staticmethod
    def recover_message_from_image(input_image: Image.Image, num_lsb: int) -> bytes:
        """Recovers the hidden message from an image using the specified number of LSBs."""
        pixels = list(input_image.getdata())
        message_bits = ""
        num_channels = len(input_image.getbands())

        for pixel in pixels:
            if num_channels == 1:
                message_bits += format(Lemma.extract_lsbs(pixel, num_lsb), f'0{num_lsb}b')
            else:
                for i in range(num_channels):
                    extracted_bits = Lemma.extract_lsbs(pixel[i], num_lsb)
                    print(
                        f"Extracting {num_lsb} LSB(s) from pixel[{i}] of {pixel[i]}: Extracted bits = {extracted_bits}")
                    message_bits += format(extracted_bits, f'0{num_lsb}b')

        # Extract the first 32 bits to get the message length
        message_length_bits = message_bits[:32]
        message_length = int(message_length_bits, 2)
        expected_message_length_bits = message_length * 8

        # Extract the actual message bits based on the expected length
        message_bits = message_bits[32:32 + expected_message_length_bits]

        # Convert bits back to bytes
        message_bytes = []
        for i in range(0, len(message_bits), 8):
            byte = message_bits[i:i + 8]
            if len(byte) == 8:
                message_bytes.append(int(byte, 2))
        print(f"Raw recovered message bits: {message_bits}")
        print(f"Raw recovered message bytes: {message_bytes}")
        return bytes(message_bytes)

    @staticmethod
    def recover_data(steg_image_path: str, output_file_path: str, num_lsb: int):
        """Recovers the hidden data from the steganographed image and saves it to a file."""
        Lemma._validate_image_format(steg_image_path)
        image = Image.open(steg_image_path)

        message = Lemma.recover_message_from_image(image, num_lsb)

        with open(output_file_path, 'wb') as file:
            file.write(message)

    @staticmethod
    def analysis(image_file_path: str, input_file_path: str = None, num_lsb: int = 1):
        """Analyzes the image to determine how much data can be hidden."""
        Lemma._validate_image_format(image_file_path)
        image = Image.open(image_file_path)
        width, height = image.size
        num_channels = len(image.getbands())

        max_bits = Lemma.max_bits_to_hide(image, num_lsb, num_channels)
        max_bytes = max_bits // 8

        print(f"Image Resolution: {width}x{height}")
        print(f"Max Bits to Hide: {max_bits}")
        print(f"Max Bytes to Hide: {max_bytes}")

        if input_file_path:
            file_size = Lemma.get_filesize(input_file_path)
            print(f"Input File Size: {file_size} bytes")

            bytes_for_file_size = Lemma.bytes_in_max_file_size(image, num_lsb, num_channels)
            print(f"Bytes needed for file size tag: {bytes_for_file_size}")

    @staticmethod
    def calculate_max_message_size(image_path: str, num_lsb: int) -> int:
        """Calculates the maximum message size in bytes that can be hidden in the image."""
        Lemma._validate_image_format(image_path)
        image = Image.open(image_path)
        width, height = image.size
        num_channels = len(image.getbands())

        total_bits = width * height * num_channels * num_lsb
        max_message_size = total_bits // 8  # Convert bits to bytes

        return max_message_size

    # Enhanced Bit Manipulation Functions #
    @staticmethod
    def set_lsbs(byte_value: int, bit_value: int, num_bits: int) -> int:
        """Set the specified number of least significant bits to the provided value."""
        mask = (1 << num_bits) - 1
        new_value = (byte_value & ~mask) | (bit_value & mask)
        print(f"Setting {num_bits} LSB(s) of {byte_value} to {bit_value}: Result = {new_value}")
        return new_value


    @staticmethod
    def extract_lsbs(byte_value: int, num_bits: int) -> int:
        """Extract the specified number of least significant bits from a byte or integer."""
        extracted_value = byte_value & ((1 << num_bits) - 1)
        print(f"Extracting {num_bits} LSB(s) from {byte_value}: Extracted = {extracted_value}")
        return extracted_value

    @staticmethod
    def set_lsbs_batch(data: list, bit_values: list, num_bits: int) -> list:
        """Set the specified number of least significant bits for each element in a list."""
        return [Lemma.set_lsbs(byte, bit, num_bits) for byte, bit in zip(data, bit_values)]

    @staticmethod
    def mask_lsbs(byte_value: int, mask: int) -> int:
        """Apply a mask to the least significant bits."""
        return byte_value & mask

    @staticmethod
    def shift_lsbs(byte_value: int, shift_by: int) -> int:
        """Shift the least significant bits to the left or right."""
        return byte_value >> shift_by if shift_by > 0 else byte_value << abs(shift_by)

# Example test execution:
if __name__ == "__main__":
    # Increase image size for more capacity
    test_image = Image.new('RGB', (4, 4), color='white')
    test_image_path = 'test_image.png'
    test_image.save(test_image_path)

    # Reduce message size to ensure it fits
    message = b'Hi'
    num_lsb = 2

    # Hide the message in the image
    image_with_message = Lemma.hide_message_in_image(test_image, message, num_lsb)
    image_with_message_path = 'image_with_message.png'
    image_with_message.save(image_with_message_path)

    # Recover the message from the image
    recovered_message = Lemma.recover_message_from_image(image_with_message, num_lsb)

    # Outputs
    print(f"Raw recovered message bytes: {recovered_message}")
    print("Recovered message:", recovered_message.decode('utf-8', errors='ignore'))