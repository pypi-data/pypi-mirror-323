import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class Encryptor:
    def __init__(self, key: str):
        """Initialize the encryptor with a key.
        
        Args:
            key: The encryption key (will be padded/truncated to 32 bytes)
        """
        # Convert key to bytes and ensure it's exactly 32 bytes
        self.key = key.encode('utf-8')[:32].ljust(32, b'\0')

    def encrypt_message(self, message: str) -> str:
        """Encrypt a message using AES-CBC with a random IV.
        
        Args:
            message: The message to encrypt
            
        Returns:
            Base64-encoded string containing IV + encrypted data
        """
        iv = get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded_data = pad(message.encode(), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        return base64.b64encode(iv + encrypted).decode('utf-8')

    def decrypt_message(self, encrypted_message: str) -> str:
        """Decrypt a message using AES-CBC.
        
        Args:
            encrypted_message: Base64-encoded string containing IV + encrypted data
            
        Returns:
            Decrypted message as string
        """
        decoded = base64.b64decode(encrypted_message)
        iv = decoded[:16]
        encrypted = decoded[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted)
        return unpad(decrypted, AES.block_size).decode('utf-8')