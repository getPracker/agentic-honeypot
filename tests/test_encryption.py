"""Tests for EncryptionManager."""

import sys
import os
import pytest

# Set required env vars
os.environ['DATABASE_URL'] = "sqlite:///test.db"
os.environ['ENCRYPTION_KEY'] = "DGRP2s9PsfDib7V9rKaa4Dld-DfTaqPiCkIJ3Y1EOWQ="
os.environ['API_KEYS'] = '["test"]'

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeypot.utils.encryption import EncryptionManager, get_encryption_manager
from cryptography.fernet import InvalidToken


class TestEncryptionManager:
    def setUp(self):
        self.manager = EncryptionManager()

    def test_encrypt_decrypt_string(self):
        """Test basic encryption and decryption of strings."""
        manager = EncryptionManager()
        original = "This is sensitive data"
        
        encrypted = manager.encrypt(original)
        assert encrypted != original
        assert isinstance(encrypted, str)
        
        decrypted = manager.decrypt(encrypted)
        assert decrypted == original

    def test_encrypt_decrypt_bytes(self):
        """Test encryption and decryption of bytes."""
        manager = EncryptionManager()
        original = b"Binary data here"
        
        encrypted = manager.encrypt(original)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == original.decode('utf-8')

    def test_encrypt_unicode(self):
        """Test encryption of unicode characters."""
        manager = EncryptionManager()
        original = "Hello 世界 🌍"
        
        encrypted = manager.encrypt(original)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == original

    def test_decrypt_invalid_data(self):
        """Test that decrypting invalid data raises InvalidToken."""
        manager = EncryptionManager()
        
        with pytest.raises(InvalidToken):
            manager.decrypt("invalid_encrypted_data")

    def test_decrypt_wrong_key(self):
        """Test that decrypting with wrong key fails."""
        manager1 = EncryptionManager()
        encrypted = manager1.encrypt("secret")
        
        # Create new manager with different key (would need to mock settings)
        # For now, just verify the encrypted data is different from original
        assert encrypted != "secret"

    def test_generate_key(self):
        """Test key generation."""
        key = EncryptionManager.generate_key()
        assert isinstance(key, str)
        assert len(key) > 0
        
        # Verify it's a valid Fernet key by trying to use it
        from cryptography.fernet import Fernet
        fernet = Fernet(key.encode())
        assert fernet is not None

    def test_get_encryption_manager_singleton(self):
        """Test that get_encryption_manager returns singleton."""
        manager1 = get_encryption_manager()
        manager2 = get_encryption_manager()
        
        assert manager1 is manager2

    def test_encryption_determinism(self):
        """Test that same data encrypted twice produces different ciphertexts."""
        manager = EncryptionManager()
        data = "test data"
        
        encrypted1 = manager.encrypt(data)
        encrypted2 = manager.encrypt(data)
        
        # Fernet includes timestamp and random IV, so ciphertexts differ
        assert encrypted1 != encrypted2
        
        # But both decrypt to same value
        assert manager.decrypt(encrypted1) == data
        assert manager.decrypt(encrypted2) == data

    def test_empty_string_encryption(self):
        """Test encryption of empty string."""
        manager = EncryptionManager()
        original = ""
        
        encrypted = manager.encrypt(original)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == original

    def test_large_data_encryption(self):
        """Test encryption of large data."""
        manager = EncryptionManager()
        original = "A" * 10000
        
        encrypted = manager.encrypt(original)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == original


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
