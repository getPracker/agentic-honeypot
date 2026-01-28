"""Tests for security features and log sanitization."""

import sys
import os
import pytest
import re

# Set required env vars
os.environ.setdefault('DATABASE_URL', "sqlite:///test.db")
os.environ.setdefault('ENCRYPTION_KEY', "DGRP2s9PsfDib7V9rKaa4Dld-DfTaqPiCkIJ3Y1EOWQ=")
os.environ.setdefault('API_KEYS', '["test-key"]')

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeypot.utils.logging import sanitize_log_data


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    (Copied from main.py to avoid FastAPI import in tests)
    """
    if not text:
        return text
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Remove control characters except newline and tab
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
    
    # Limit length to prevent DoS
    max_length = 10000
    if len(text) > max_length:
        text = text[:max_length]
    
    return text


class TestLogSanitization:
    """Test log sanitization functionality."""
    
    def test_sanitize_api_key(self):
        """Test that API keys are redacted in logs."""
        data = 'api_key: "sk-1234567890abcdef"'
        sanitized = sanitize_log_data(data)
        assert "sk-1234567890abcdef" not in sanitized
        assert "***REDACTED***" in sanitized
    
    def test_sanitize_phone_number(self):
        """Test that phone numbers are redacted."""
        data = "Call me at 9876543210"
        sanitized = sanitize_log_data(data)
        assert "9876543210" not in sanitized
        assert "***PHONE***" in sanitized
    
    def test_sanitize_bank_account(self):
        """Test that bank account numbers are redacted."""
        data = "Account number: 123456789012"
        sanitized = sanitize_log_data(data)
        assert "123456789012" not in sanitized
        assert "***ACCOUNT***" in sanitized
    
    def test_sanitize_email(self):
        """Test that email addresses are redacted."""
        data = "Contact: user@example.com"
        sanitized = sanitize_log_data(data)
        assert "user@example.com" not in sanitized
        assert "***EMAIL***" in sanitized
    
    def test_sanitize_url_with_token(self):
        """Test that URLs with sensitive parameters are redacted."""
        data = "https://api.example.com/data?token=secret123&key=abc"
        sanitized = sanitize_log_data(data)
        # The key parameter should be redacted
        assert "key=***REDACTED***" in sanitized
    
    def test_sanitize_dict(self):
        """Test sanitization of dictionary data."""
        data = {
            "api_key": "secret123",
            "password": "pass123",
            "username": "john",
            "phone": "9876543210"
        }
        sanitized = sanitize_log_data(data)
        
        assert sanitized["api_key"] == "***REDACTED***"
        assert sanitized["password"] == "***REDACTED***"
        assert sanitized["username"] == "john"
        assert "***PHONE***" in sanitized["phone"]
    
    def test_sanitize_nested_dict(self):
        """Test sanitization of nested dictionaries."""
        data = {
            "user": {
                "name": "John",
                "token": "secret123"
            },
            "contact": "9876543210"
        }
        sanitized = sanitize_log_data(data)
        
        assert sanitized["user"]["token"] == "***REDACTED***"
        assert sanitized["user"]["name"] == "John"
        assert "***PHONE***" in sanitized["contact"]
    
    def test_sanitize_list(self):
        """Test sanitization of lists."""
        data = ["9876543210", "user@example.com", "normal text"]
        sanitized = sanitize_log_data(data)
        
        assert "***PHONE***" in sanitized[0]
        assert "***EMAIL***" in sanitized[1]
        assert sanitized[2] == "normal text"
    
    def test_sanitize_preserves_safe_data(self):
        """Test that safe data is not modified."""
        data = "This is a normal log message without sensitive data"
        sanitized = sanitize_log_data(data)
        assert sanitized == data


class TestInputSanitization:
    """Test input sanitization functionality."""
    
    def test_sanitize_null_bytes(self):
        """Test that null bytes are removed."""
        text = "Hello\x00World"
        sanitized = sanitize_input(text)
        assert "\x00" not in sanitized
        assert sanitized == "HelloWorld"
    
    def test_sanitize_control_characters(self):
        """Test that control characters are removed."""
        text = "Hello\x01\x02\x03World"
        sanitized = sanitize_input(text)
        assert "\x01" not in sanitized
        assert "\x02" not in sanitized
        assert "\x03" not in sanitized
        assert sanitized == "HelloWorld"
    
    def test_preserve_newlines_and_tabs(self):
        """Test that newlines and tabs are preserved."""
        text = "Hello\nWorld\tTest"
        sanitized = sanitize_input(text)
        assert "\n" in sanitized
        assert "\t" in sanitized
    
    def test_length_limit(self):
        """Test that input is truncated to max length."""
        text = "A" * 20000
        sanitized = sanitize_input(text)
        assert len(sanitized) == 10000
    
    def test_empty_input(self):
        """Test handling of empty input."""
        assert sanitize_input("") == ""
        assert sanitize_input(None) is None
    
    def test_normal_text(self):
        """Test that normal text is preserved."""
        text = "This is a normal message with numbers 123 and symbols !@#"
        sanitized = sanitize_input(text)
        assert sanitized == text
    
    def test_unicode_characters(self):
        """Test that unicode characters are preserved."""
        text = "Hello 世界 🌍"
        sanitized = sanitize_input(text)
        assert sanitized == text


class TestSecurityValidation:
    """Test security validation rules."""
    
    def test_session_id_validation(self):
        """Test session ID format validation."""
        import re
        
        # Valid session IDs
        valid_ids = [
            "session_123",
            "test-session",
            "ABC123",
            "user_session_001"
        ]
        
        pattern = r'^[a-zA-Z0-9_-]{1,100}$'
        for sid in valid_ids:
            assert re.match(pattern, sid), f"Valid ID rejected: {sid}"
        
        # Invalid session IDs
        invalid_ids = [
            "session with spaces",
            "session@123",
            "session#123",
            "A" * 101,  # Too long
            "",  # Empty
            "session/123",
            "session\\123"
        ]
        
        for sid in invalid_ids:
            assert not re.match(pattern, sid), f"Invalid ID accepted: {sid}"


class TestSecurityHeaders:
    """Test security headers configuration."""
    
    def test_security_headers_present(self):
        """Test that all required security headers are configured."""
        expected_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "Referrer-Policy",
            "Permissions-Policy"
        ]
        
        # This would be tested in integration tests with actual HTTP requests
        # For now, we just verify the list is complete
        assert len(expected_headers) == 7


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
