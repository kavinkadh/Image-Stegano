import unittest
import os
import random
import string
from PIL import Image
from lemma_module import Lemma  # Assuming Lemma functions are in lemma_module.py

class TestLemma(unittest.TestCase):

    def setUp(self):
        """Set up common test variables."""
        self.width = 100  # Example width
        self.height = 100  # Example height
        self.num_lsb = 2   # Number of LSBs to use
        self.image_mode = 'RGB'  # Example mode (RGB, RGBA, etc.)
        self.payload_size = 1000  # Size of the payload in bytes
        self.image_path = 'test_image.png'
        self.payload_path = 'test_payload.bin'
        self.steg_image_path = 'steg_image.png'
        self.output_payload_path = 'recovered_payload.bin'

    def generate_random_image(self, width, height, mode):
        """Generates a random image for testing."""
        image = Image.new(mode, (width, height))
        num_channels = len(mode)  # 'RGB' -> 3, 'RGBA' -> 4, 'L' -> 1

        pixels = []
        for _ in range(width * height):
            if num_channels == 1:  # Grayscale image
                pixels.append(random.randint(0, 255))
            else:  # RGB or RGBA image
                pixels.append(tuple(random.randint(0, 255) for _ in range(num_channels)))

        image.putdata(pixels)
        image.save(self.image_path)
        return self.image_path

    def generate_random_payload(self, size):
        """Generates a random payload for testing."""
        payload = os.urandom(size)
        with open(self.payload_path, 'wb') as f:
            f.write(payload)
        return self.payload_path

    def test_hide_and_recover_data(self):
        """Test the hide_data and recover_data functions."""
        # Generate random image and payload
        self.generate_random_image(self.width, self.height, self.image_mode)
        self.generate_random_payload(self.payload_size)

        # Hide the payload in the image
        Lemma.hide_data(self.image_path, self.payload_path, self.steg_image_path, self.num_lsb)

        # Recover the payload from the image
        Lemma.recover_data(self.steg_image_path, self.output_payload_path, self.num_lsb)

        # Check that the recovered payload matches the original
        with open(self.payload_path, 'rb') as original_file:
            original_payload = original_file.read()

        with open(self.output_payload_path, 'rb') as recovered_file:
            recovered_payload = recovered_file.read()

        if original_payload != recovered_payload:
            min_length = min(len(original_payload), len(recovered_payload))
            difference_index = next((i for i in range(min_length) if original_payload[i] != recovered_payload[i]), None)

            if difference_index is None:
                print("Payloads are the same for the first", min_length, "bytes.")
            else:
                print(f"Difference starts at byte index: {difference_index}")

            print(f"Original payload length: {len(original_payload)}")
            print(f"Recovered payload length: {len(recovered_payload)}")
            print(f"Original payload (first 100 bytes): {original_payload[:100]}")
            print(f"Recovered payload (first 100 bytes): {recovered_payload[:100]}")

        self.assertEqual(original_payload, recovered_payload)

    def test_exceed_storage_capacity(self):
        """Test that an error is raised when payload exceeds image capacity."""
        # Generate random image with small capacity
        self.generate_random_image(10, 10, self.image_mode)
        self.generate_random_payload(10000)  # Large payload that exceeds capacity

        with self.assertRaises(ValueError):
            Lemma.hide_data(self.image_path, self.payload_path, self.steg_image_path, self.num_lsb)

    def test_cross_format_steganography(self):
        """Test consistency across different image formats."""
        for mode in ['RGB', 'RGBA', 'L']:  # Test RGB, RGBA, and Grayscale
            self.image_mode = mode
            print(f"Testing mode: {mode}")

            # Generate random image and payload
            self.generate_random_image(self.width, self.height, self.image_mode)
            self.generate_random_payload(self.payload_size)

            # Log the initial pixels
            original_image = Image.open(self.image_path)
            print(f"Sample original pixels ({mode}):", list(original_image.getdata())[:10])

            # Hide the payload in the image
            Lemma.hide_data(self.image_path, self.payload_path, self.steg_image_path, self.num_lsb)

            # Log the modified pixels
            steg_image = Image.open(self.steg_image_path)
            print(f"Sample modified pixels ({mode}):", list(steg_image.getdata())[:10])

            # Recover the payload from the image
            Lemma.recover_data(self.steg_image_path, self.output_payload_path, self.num_lsb)

            with open(self.payload_path, 'rb') as original_file:
                original_payload = original_file.read()

            with open(self.output_payload_path, 'rb') as recovered_file:
                recovered_payload = recovered_file.read()

            # Additional Diagnostic Print Statements
            if original_payload != recovered_payload:
                print(f"Test failed for image mode: {mode}")
                min_length = min(len(original_payload), len(recovered_payload))
                difference_index = next((i for i in range(min_length) if original_payload[i] != recovered_payload[i]),
                                        None)

                if difference_index is None:
                    print(f"Payloads are the same for the first {min_length} bytes.")
                else:
                    print(f"Difference starts at byte index: {difference_index}")

                print(f"Original payload length: {len(original_payload)}")
                print(f"Recovered payload length: {len(recovered_payload)}")
                print(f"Original payload (first 100 bytes): {original_payload[:100]}")
                print(f"Recovered payload (first 100 bytes): {recovered_payload[:100]}")

            self.assertEqual(original_payload, recovered_payload, f"Failed for mode: {mode}")

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.image_path):
            os.remove(self.image_path)
        if os.path.exists(self.payload_path):
            os.remove(self.payload_path)
        if os.path.exists(self.steg_image_path):
            os.remove(self.steg_image_path)
        if os.path.exists(self.output_payload_path):
            os.remove(self.output_payload_path)

if __name__ == '__main__':
    unittest.main()
