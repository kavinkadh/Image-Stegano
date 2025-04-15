from sierra_module import Sierra
from PIL import Image
import numpy as np

# Create a simple 3x3 image for testing
test_image = Image.new('RGB', (3, 3), color=(255, 0, 0))
test_image_path = 'test_image.png'
test_image.save(test_image_path)

# Test 1: Check if LSB steganography is detected
steganography_detected = Sierra.is_lsb_steganography(test_image_path, num_lsb=2)
print(f"Steganography Detected: {steganography_detected}")

# Test 2: Analyze LSB distribution in the image
lsb_distributions = Sierra.analyze_lsb_distribution(test_image_path, num_lsb=2)
print(f"LSB Distributions: {lsb_distributions}")
