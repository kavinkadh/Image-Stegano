import cv2
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from scipy.stats import norm, chisquare
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os


class Sierra:
    @staticmethod
    def is_lsb_steganography(image_path: str, num_lsb: int = 1) -> bool:
        """
        Determines if an image likely contains LSB steganographic data.
        Analyzes multiple LSB layers and uses statistical tests.
        """
        image = Image.open(image_path)
        pixels = np.array(image)

        lsb_values = pixels & ((1 << num_lsb) - 1)
        lsb_flat = lsb_values.flatten()
        unique, counts = np.unique(lsb_flat, return_counts=True)
        distribution = dict(zip(unique, counts))

        total_bits = pixels.size * num_lsb
        threshold = 0.1 * total_bits  # 10% deviation

        if len(distribution) != (1 << num_lsb):
            return True

        for count in distribution.values():
            if abs(count - total_bits // (1 << num_lsb)) > threshold:
                return True

        return False

    @staticmethod
    def analyze_lsb_distribution(image_path: str, num_lsb: int = 1):
        """
        Analyzes the distribution of LSBs in the image across multiple layers.
        """
        image = Image.open(image_path)
        pixels = np.array(image)

        for i in range(1, num_lsb + 1):
            lsb_values = pixels & ((1 << i) - 1)
            lsb_flat = lsb_values.flatten()
            unique, counts = np.unique(lsb_flat, return_counts=True)
            distribution = dict(zip(unique, counts))

            print(f"LSB Distribution for {i} LSB(s):")
            for lsb_value, count in distribution.items():
                print(f"Value {lsb_value}: {count} times")

        return distribution

    @staticmethod
    def show_lsb(image_path: str, n: int):
        """
        Visualizes the n LSBs of an image and saves the result as a new image.
        """
        image = Image.open(image_path)
        pixels = np.array(image)

        lsb_values = pixels & ((1 << n) - 1)
        lsb_values = lsb_values * (255 // ((1 << n) - 1))

        lsb_image = Image.fromarray(lsb_values.astype(np.uint8))

        base_name, ext = os.path.splitext(image_path)
        new_image_path = f"{base_name}_{n}LSBs{ext}"

        lsb_image.save(new_image_path)
        return new_image_path

    @staticmethod
    def rs_analysis(image_path: str, num_lsb: int = 1) -> float:
        """
        Performs RS analysis to detect steganography in LSBs.
        Returns a metric indicating the likelihood of steganography.
        """
        image = Image.open(image_path)
        pixels = np.array(image)

        def flipping_mask(pixels, mask):
            flipped = pixels ^ mask
            return flipped

        def calculate_rs(pixels):
            regular, singular = 0, 0
            for x in range(0, len(pixels) - 1):
                for y in range(0, len(pixels[0]) - 1):
                    block = pixels[x:x + 2, y:y + 2]
                    flipped = flipping_mask(block, 1)
                    regular += np.sum(block == flipped)
                    singular += np.sum(block != flipped)
            return regular, singular

        r, s = calculate_rs(pixels)
        if r + s == 0:
            return 0
        return r / (r + s)

    @staticmethod
    def spatial_analysis(image_path: str):
        """
        Applies edge detection and spatial analysis to detect anomalies in the image.
        """
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        edges = cv2.Canny(image, 100, 200)

        plt.imshow(edges, cmap='gray')
        plt.title('Edge Detection')
        plt.show()

    @staticmethod
    def ml_detection(image_paths, labels):
        """
        Trains a simple ML model to detect steganography in images.
        Uses edge detection and LSB analysis as features.
        """
        features = []
        for image_path in image_paths:
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            edges = cv2.Canny(image, 100, 200)
            edge_hist = np.histogram(edges, bins=256)[0]

            pixels = np.array(Image.open(image_path))
            lsb_values = pixels & 1
            lsb_hist = np.histogram(lsb_values, bins=256)[0]

            features.append(np.concatenate([edge_hist, lsb_hist]))

        X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

        clf = RandomForestClassifier()
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)

        print(classification_report(y_test, y_pred))

        return clf

    @staticmethod
    def detect_frequency_domain_steganography(image_path: str):
        """
        Detects potential steganography in the frequency domain (e.g., DCT coefficients in JPEG images).
        """
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        dct = cv2.dct(np.float32(image) / 255.0)

        plt.imshow(np.log(np.abs(dct)), cmap='gray')
        plt.title('DCT Coefficients')
        plt.show()

# Example usage (commented out for execution in PCI):
# Sierra.spatial_analysis('input_image.png')
# Sierra.ml_detection(['image1.png', 'image2.png'], [0, 1])
# Sierra.detect_frequency_domain_steganography('input_image.jpg')

