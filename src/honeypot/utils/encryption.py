"""Encryption utilities for secure data storage."""

import base64
import logging
from typing import Union
from cryptography.fernet import Fernet, InvalidToken

from ..config import get_settings

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Manages encryption and decryption of sensitive data."""
    
    def __init__(self):
        """Initialize encryption manager with configured key."""
        settings = get_settings()
        # The key from settings is already a base64-encoded string
        # Fernet expects bytes
        key = settings.encryption_key
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        try:
            self._fernet = Fernet(key)
        except Exception as e:
            logger.error(f"Failed to initialize Fernet with provided key: {e}")
            raise ValueError("Invalid encryption key format. Must be a valid Fernet key.")
    
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
        
        try:
            encrypted = self._fernet.encrypt(data)
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt base64 encoded encrypted data.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted string
            
        Raises:
            InvalidToken: If decryption fails (wrong key or corrupted data)
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except InvalidToken:
            logger.error("Decryption failed: Invalid token or wrong key")
            raise
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
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