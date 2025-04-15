import unittest
import random
from bravo_module import Bravo  # Import the Bravo class

class TestBravo(unittest.TestCase):

    def setUp(self):
        """Set up the common variables for the tests."""
        self.payload = b'\xDE\xAD\xBE\xEF'  # Example payload
        self.carrier = bytearray([0xFF] * 16)  # Example carrier with 16 bytes
        self.num_lsb = 2  # Number of LSBs to use for hiding the payload
        self.byte_depth = 1  # Assume 8-bit depth for initial testing

    def test_interleave_deinterleave(self):
        """Test that interleaving and deinterleaving process is correct."""
        interleaved_carrier = Bravo.lsb_interleave_bytes(self.carrier, self.payload, self.num_lsb, truncate=False)
        recovered_payload = Bravo.lsb_deinterleave_bytes(interleaved_carrier, len(self.payload) * 8, self.num_lsb)

        # Verify that the recovered payload matches the original
        self.assertEqual(self.payload, recovered_payload)

        # Verify that the length of the carrier remains unchanged
        self.assertEqual(len(interleaved_carrier), len(self.carrier))

    def test_truncated_interleave(self):
        """Test interleaving with truncation and ensure correct payload recovery."""
        interleaved_carrier = Bravo.lsb_interleave_bytes(self.carrier, self.payload, self.num_lsb, truncate=True)
        recovered_payload = Bravo.lsb_deinterleave_bytes(interleaved_carrier, len(self.payload) * 8, self.num_lsb)

        # Verify that the recovered payload matches the original
        self.assertEqual(self.payload, recovered_payload)

        # Verify that the interleaved carrier is smaller due to truncation
        self.assertLessEqual(len(interleaved_carrier), len(self.carrier))

    def test_different_byte_depths(self):
        """Test interleaving and deinterleaving across different byte depths."""
        for byte_depth in [1, 2, 3]:  # Test 8-bit, 16-bit, and 24-bit depths
            interleaved_carrier = Bravo.lsb_interleave_bytes(self.carrier, self.payload, self.num_lsb, byte_depth=byte_depth)
            recovered_payload = Bravo.lsb_deinterleave_bytes(interleaved_carrier, len(self.payload) * 8, self.num_lsb, byte_depth=byte_depth)

            # Verify that the recovered payload matches the original
            self.assertEqual(self.payload, recovered_payload)

    def test_random_data(self):
        """Test interleaving and deinterleaving with random data."""
        random_carrier = bytearray([random.randint(0, 255) for _ in range(16)])
        interleaved_carrier = Bravo.lsb_interleave_bytes(random_carrier, self.payload, self.num_lsb)
        recovered_payload = Bravo.lsb_deinterleave_bytes(interleaved_carrier, len(self.payload) * 8, self.num_lsb)

        # Verify that the recovered payload matches the original
        self.assertEqual(self.payload, recovered_payload)

    def test_empty_payload(self):
        """Test how functions handle an empty payload."""
        empty_payload = b''
        interleaved_carrier = Bravo.lsb_interleave_bytes(self.carrier, empty_payload, self.num_lsb)
        recovered_payload = Bravo.lsb_deinterleave_bytes(interleaved_carrier, len(empty_payload) * 8, self.num_lsb)

        # Verify that the recovered payload is also empty
        self.assertEqual(empty_payload, recovered_payload)

    def test_maximum_capacity(self):
        """Test interleaving a payload that exactly matches the carrier's capacity."""
        max_capacity_payload = bytes([0xAA] * (len(self.carrier) * self.num_lsb // 8))
        interleaved_carrier = Bravo.lsb_interleave_bytes(self.carrier, max_capacity_payload, self.num_lsb)
        recovered_payload = Bravo.lsb_deinterleave_bytes(interleaved_carrier, len(max_capacity_payload) * 8, self.num_lsb)

        # Verify that the recovered payload matches the original
        self.assertEqual(max_capacity_payload, recovered_payload)

    def test_oversized_payload(self):
        """Test how the function handles a payload too large for the carrier."""
        oversized_payload = bytes([0xAA] * ((len(self.carrier) * self.num_lsb // 8) + 1))

        with self.assertRaises(ValueError):
            Bravo.lsb_interleave_bytes(self.carrier, oversized_payload, self.num_lsb)

    def test_invalid_num_lsb(self):
        """Test how the functions handle invalid `num_lsb` values."""
        with self.assertRaises(ValueError):
            Bravo.lsb_interleave_bytes(self.carrier, self.payload, 0)  # Invalid because num_lsb cannot be 0

        with self.assertRaises(ValueError):
            Bravo.lsb_interleave_bytes(self.carrier, self.payload, 9)  # Invalid because num_lsb > 8 (for byte_depth = 1)

    def test_invalid_input_types(self):
        """Test how the functions handle invalid input types."""
        with self.assertRaises(TypeError):
            Bravo.lsb_interleave_bytes("not_bytes", self.payload, self.num_lsb)  # Carrier is not bytes

        with self.assertRaises(TypeError):
            Bravo.lsb_deinterleave_bytes("not_bytes", len(self.payload) * 8, self.num_lsb)  # Carrier is not bytes

    def test_performance_large_payload(self):
        """Test performance with a large payload and carrier."""
        large_carrier = bytearray([0xFF] * (10**6))  # Large carrier with 1,000,000 bytes
        large_payload = bytes([0xAA] * (10**5))  # Large payload with 100,000 bytes

        interleaved_carrier = Bravo.lsb_interleave_bytes(large_carrier, large_payload, self.num_lsb)
        recovered_payload = Bravo.lsb_deinterleave_bytes(interleaved_carrier, len(large_payload) * 8, self.num_lsb)

        # Verify that the recovered payload matches the original
        self.assertEqual(large_payload, recovered_payload)

if __name__ == '__main__':
    unittest.main()