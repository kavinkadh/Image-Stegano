class Sierra:

    @staticmethod
    def is_lsb_steganography(image_path: str, num_lsb: int = 1) -> bool:
        """Determines if an image likely contains LSB steganographic data."""
        image = Image.open(image_path)
        width, height = image.size
        pixels = np.array(image)

        # Extract the LSBs of the image
        lsb_values = pixels & ((1 << num_lsb) - 1)

        # Flatten the LSB array and analyze the distribution of 0s and 1s
        lsb_flat = lsb_values.flatten()
        unique, counts = np.unique(lsb_flat, return_counts=True)
        distribution = dict(zip(unique, counts))

        # We expect an even distribution of LSBs if no data is hidden
        total_bits = width * height * pixels.shape[2] * num_lsb
        threshold = 0.1 * total_bits  # 10% deviation is allowed

        if len(distribution) != (1 << num_lsb):
            # If the number of unique values is not what we expect, it's suspicious
            return True

        for count in distribution.values():
            if abs(count - total_bits // (1 << num_lsb)) > threshold:
                return True

        return False

    @staticmethod
    def analyze_lsb_distribution(image_path: str, num_lsb: int = 1):
        """Analyzes the distribution of LSBs in the image."""
        image = Image.open(image_path)
        pixels = np.array(image)

        # Extract the LSBs of the image
        lsb_values = pixels & ((1 << num_lsb) - 1)

        # Flatten the LSB array and count occurrences of each LSB value
        lsb_flat = lsb_values.flatten()
        unique, counts = np.unique(lsb_flat, return_counts=True)
        distribution = dict(zip(unique, counts))

        # Report the LSB distribution
        print(f"LSB Distribution for {num_lsb} LSB(s):")
        for lsb_value, count in distribution.items():
            print(f"Value {lsb_value}: {count} times")

        return distribution

    @staticmethod
    def show_lsb(image_path: str, n: int):
        """Visualizes the n LSBs of an image and saves the result as a new image."""
        image = Image.open(image_path)
        pixels = np.array(image)

        # Isolate the n least significant bits of each color channel
        lsb_values = pixels & ((1 << n) - 1)

        # Scale the LSB values to make them visible (e.g., shift them to the most significant bits)
        lsb_values = lsb_values * (255 // ((1 << n) - 1))

        # Create a new image from the LSB values
        lsb_image = Image.fromarray(lsb_values.astype(np.uint8))

        # Construct the new filename
        base_name, ext = os.path.splitext(image_path)
        new_image_path = f"{base_name}_{n}LSBs{ext}"

        # Save the new image
        lsb_image.save(new_image_path)
        return new_image_path

# Example usage:
# distribution = Sierra.analyze_lsb_distribution('input_image.png', 2)
