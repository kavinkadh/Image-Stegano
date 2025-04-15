import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from Steganography.CryptoStegoManager import CryptoStegoManager

# Add the Steganography folder to sys.path
sys.path.append(os.path.abspath("Steganography"))

class StegoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CryptoStegoManager - Tkinter GUI")
        self.root.geometry("500x400")

        # Labels and buttons
        self.create_widgets()

    def create_widgets(self):
        # Title label
        tk.Label(self.root, text="CryptoStegoManager - Steganography Tool", font=("Arial", 16)).pack(pady=10)

        # Embed button
        tk.Button(self.root, text="Embed Message.txt", command=self.embed_message).pack(pady=10)

        # Extract button
        tk.Button(self.root, text="Extract Message.txt", command=self.extract_message).pack(pady=10)

    def embed_message(self):
        # Prompt user for the carrier image and the message file
        carrier_path = filedialog.askopenfilename(title="Select Carrier Image", filetypes=[("Image Files", "*.png;*.bmp")])
        if not carrier_path:
            return

        message_path = filedialog.askopenfilename(title="Select Message.txt/File to Embed", filetypes=[("All Files", "*.*")])
        if not message_path:
            return

        # Ask user for output location
        output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")], title="Save Stego Image As")
        if not output_path:
            return

        # Ask for encryption method
        encryption_method = simpledialog.askstring("Encryption Method", "Enter Encryption Method (AES or FERNET):")
        key = simpledialog.askstring("Encryption Key", "Enter Encryption Key:")

        if not encryption_method or not key:
            messagebox.showerror("Error", "Encryption method and key are required.")
            return

        try:
            # Embed the message
            CryptoStegoManager.embed_message(
                carrier_path=carrier_path,
                input_path=message_path,
                output_path=output_path,
                key=key,
                encryption_method=encryption_method
            )
            messagebox.showinfo("Success", f"Message.txt embedded successfully. Stego image saved at: {output_path}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def extract_message(self):
        # Prompt user for the stego image
        stego_path = filedialog.askopenfilename(title="Select Stego Image", filetypes=[("Image Files", "*.png;*.bmp")])
        if not stego_path:
            return

        # Ask user for output location
        output_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], title="Save Extracted Message.txt As")
        if not output_path:
            return

        # Ask for encryption method
        encryption_method = simpledialog.askstring("Encryption Method", "Enter Encryption Method (AES or FERNET):")
        key = simpledialog.askstring("Encryption Key", "Enter Encryption Key:")

        if not encryption_method or not key:
            messagebox.showerror("Error", "Encryption method and key are required.")
            return

        try:
            # Extract the message
            CryptoStegoManager.extract_message(
                stego_path=stego_path,
                output_path=output_path,
                key=key,
                encryption_method=encryption_method
            )
            messagebox.showinfo("Success", f"Message.txt extracted successfully. Saved at: {output_path}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = StegoApp(root)
    root.mainloop()
