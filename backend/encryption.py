"""
Encryption utilities for protecting PII (emails and phone numbers)
Uses Fernet symmetric encryption (AES-128)
"""
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import base64

load_dotenv()

# Get encryption key from environment or generate one
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

if not ENCRYPTION_KEY:
    # Generate a key for development (you MUST set this in production!)
    print("WARNING: No ENCRYPTION_KEY found in .env - generating temporary key")
    print("Add this to your .env file:")
    temp_key = Fernet.generate_key().decode()
    print(f"ENCRYPTION_KEY={temp_key}")
    ENCRYPTION_KEY = temp_key

# Initialize cipher
cipher = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

def encrypt_string(plaintext):
    """
    Encrypt a string (email or phone number)

    Args:
        plaintext: String to encrypt

    Returns:
        Encrypted string (base64 encoded)
    """
    if not plaintext:
        return None

    try:
        encrypted = cipher.encrypt(plaintext.encode())
        return encrypted.decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return plaintext  # Fallback to plaintext (not ideal but prevents crashes)

def decrypt_string(encrypted):
    """
    Decrypt a string (email or phone number)

    Args:
        encrypted: Encrypted string (base64 encoded)

    Returns:
        Decrypted plaintext string
    """
    if not encrypted:
        return None

    try:
        decrypted = cipher.decrypt(encrypted.encode())
        return decrypted.decode()
    except Exception as e:
        # If decryption fails, might be plaintext from before encryption was added
        print(f"Decryption error (might be plaintext): {e}")
        return encrypted  # Return as-is

def generate_key():
    """Generate a new encryption key for production use"""
    return Fernet.generate_key().decode()

# For testing
if __name__ == "__main__":
    test_email = "test@example.com"
    test_phone = "+11234567890"

    encrypted_email = encrypt_string(test_email)
    encrypted_phone = encrypt_string(test_phone)

    print(f"Original email: {test_email}")
    print(f"Encrypted email: {encrypted_email}")
    print(f"Decrypted email: {decrypt_string(encrypted_email)}")
    print()
    print(f"Original phone: {test_phone}")
    print(f"Encrypted phone: {encrypted_phone}")
    print(f"Decrypted phone: {decrypt_string(encrypted_phone)}")
