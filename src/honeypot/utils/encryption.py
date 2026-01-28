"""Encryption utilities for secure data storage."""

import base64
from typing import Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..config import get_settings


class EncryptionManager:
    """Manages encryption and decryption of sensitive data."""
    
    def __init__(self):
        """Initialize encryption manager with configured key."""
        settings = get_settings()
        self._fernet = Fernet(settings.encryption_key.encode())
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        Encrypt data and return base64 encoded string.
        
        Args:
            data: Data to encrypt (string or bytes)
            
        Returns:
            Base64 encoded encrypted data
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted = self._fernet.encrypt(data)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt base64 encoded encrypted data.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted string
        """
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted = self._fernet.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key."""
        return Fernet.generate_key().decode('utf-8')


# Global encryption manager instance
_encryption_manager = None


def get_encryption_manager() -> EncryptionManager:
    """Get the global encryption manager instance."""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager