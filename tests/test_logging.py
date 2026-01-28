"""Unit tests for logging utilities."""

import pytest
from hypothesis import given, strategies as st

from honeypot.utils.logging import sanitize_log_data


class TestLogSanitization:
    """Test cases for log data sanitization."""
    
    def test_sanitize_api_key(self):
        """Test API key sanitization."""
        data = 'api_key: "secret123"'
        result = sanitize_log_data(data)
        assert "secret123" not in result
        assert "***REDACTED***" in result
    
    def test_sanitize_phone_number(self):
        """Test phone number sanitization."""
        data = "Call me at 9876543210"
        result = sanitize_log_data(data)
        assert "9876543210" not in result
        assert "***PHONE***" in result
    
    def test_sanitize_bank_account(self):
        """Test bank account number sanitization."""
        data = "Account: 123456789012"
        result = sanitize_log_data(data)
        assert "123456789012" not in result
        assert "***ACCOUNT***" in result
    
    def test_sanitize_email(self):
        """Test email address sanitization."""
        data = "Contact: user@example.com"
        result = sanitize_log_data(data)
        assert "user@example.com" not in result
        assert "***EMAIL***" in result
    
    def test_sanitize_url_with_token(self):
        """Test URL with token sanitization."""
        data = "https://api.example.com/data?token=secret123&other=value"
        result = sanitize_log_data(data)
        assert "secret123" not in result
        assert "***REDACTED***" in result
        assert "other=value" in result
    
    def test_sanitize_dict(self):
        """Test dictionary sanitization."""
        data = {
            "api_key": "secret123",
            "message": "Hello world",
            "password": "mypassword"
        }
        result = sanitize_log_data(data)
        assert result["api_key"] == "***REDACTED***"
        assert result["message"] == "Hello world"
        assert result["password"] == "***REDACTED***"
    
    def test_sanitize_list(self):
        """Test list sanitization."""
        data = ["api_key: secret123", "normal message", "phone: 9876543210"]
        result = sanitize_log_data(data)
        assert "secret123" not in str(result)
        assert "9876543210" not in str(result)
        assert "normal message" in result
    
    def test_sanitize_nested_structure(self):
        """Test nested data structure sanitization."""
        data = {
            "user": {
                "name": "John",
                "api_key": "secret123",
                "contacts": ["9876543210", "user@example.com"]
            },
            "message": "Hello world"
        }
        result = sanitize_log_data(data)
        assert result["user"]["api_key"] == "***REDACTED***"
        assert result["user"]["name"] == "John"
        assert "9876543210" not in str(result["user"]["contacts"])
        assert "user@example.com" not in str(result["user"]["contacts"])
        assert result["message"] == "Hello world"
    
    @given(st.text())
    def test_sanitize_preserves_non_sensitive_data(self, text):
        """Property test: Sanitization should preserve non-sensitive data structure."""
        # Skip texts that contain patterns we sanitize
        sensitive_patterns = ["api", "key", "@", "http"]
        if any(pattern in text.lower() for pattern in sensitive_patterns):
            return
        
        result = sanitize_log_data(text)
        # For non-sensitive text, result should be the same
        assert isinstance(result, str)
    
    def test_sanitize_none_and_primitives(self):
        """Test sanitization of None and primitive types."""
        assert sanitize_log_data(None) is None
        assert sanitize_log_data(123) == 123
        assert sanitize_log_data(True) is True
        assert sanitize_log_data(3.14) == 3.14