from PIL import Image
from lemma_module import Lemma

# Parameters
secret_image_path = 'Secret_Image.png'
num_lsb = 2

# Step 1: Open the secret image (the Labrador dog image with the hidden message)
secret_image = Image.open(secret_image_path)

# Step 2: Recover the message from the image
recovered_message = Lemma.recover_message_from_image(secret_image, num_lsb)

# Step 3: Output the recovered message
print("Recovered message:", recovered_message.decode('utf-8', errors='ignore'))
