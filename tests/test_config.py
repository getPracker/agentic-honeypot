"""Unit tests for configuration management."""

import pytest
import os
from unittest.mock import patch

from honeypot.config import Settings, get_settings


class TestSettings:
    """Test cases for Settings configuration."""
    
    def test_default_settings(self):
        """Test default settings values."""
        with patch.dict(os.environ, {
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "ENCRYPTION_KEY": "test-key-32-bytes-long-for-testing"
        }):
            settings = Settings()
            assert settings.api_host == "0.0.0.0"
            assert settings.api_port == 8000
            assert settings.log_level == "INFO"
            assert settings.max_concurrent_sessions == 100
    
    def test_environment_override(self):
        """Test environment variable override."""
        with patch.dict(os.environ, {
            "API_HOST": "127.0.0.1",
            "API_PORT": "9000",
            "LOG_LEVEL": "DEBUG",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "ENCRYPTION_KEY": "test-key-32-bytes-long-for-testing"
        }):
            settings = Settings()
            assert settings.api_host == "127.0.0.1"
            assert settings.api_port == 9000
            assert settings.log_level == "DEBUG"
    
    def test_api_keys_parsing(self):
        """Test API keys parsing from JSON array string."""
        with patch.dict(os.environ, {
            "API_KEYS": '["key1", "key2", "key3"]',
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "ENCRYPTION_KEY": "test-key-32-bytes-long-for-testing"
        }):
            settings = Settings()
            assert settings.api_keys == ["key1", "key2", "key3"]
    
    def test_api_keys_with_spaces(self):
        """Test API keys parsing with JSON format."""
        with patch.dict(os.environ, {
            "API_KEYS": '["key1", "key2", "key3"]',
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "ENCRYPTION_KEY": "test-key-32-bytes-long-for-testing"
        }):
            settings = Settings()
            assert settings.api_keys == ["key1", "key2", "key3"]
    
    def test_get_settings_caching(self):
        """Test that get_settings returns cached instance."""
        with patch.dict(os.environ, {
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "ENCRYPTION_KEY": "test-key-32-bytes-long-for-testing"
        }):
            settings1 = get_settings()
            settings2 = get_settings()
            assert settings1 is settings2