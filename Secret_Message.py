from PIL import Image
from lemma_module import Lemma

# Use the actual path to your Labrador dog image
image = Image.open('C:\\Users\\kadhi\\Kavin\\Python\\ImageSteganography\\Steganography\\labrador_dog.png')
message = b'SRM 2nd Review'
num_lsb = 2
image_with_message = Lemma.hide_message_in_image(image, message, num_lsb)
# Load the original image
image_with_message.save('C:\\Users\\kadhi\\Kavin\\Python\\ImageSteganography\\Steganography\\Secret_Image.png', format='PNG', compress_level=0)

print("Secret image saved.")

# Print original image mode and size
