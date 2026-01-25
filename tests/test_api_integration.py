"""Integration tests for API Gateway with authentication."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime

from honeypot.main import create_app
from honeypot.models.core import MessageRequest, Message, RequestMetadata


class TestAPIIntegration:
    """Test cases for API Gateway integration."""
    
    @patch('honeypot.main.setup_logging')
    @patch('honeypot.main.get_logger')
    @patch('honeypot.main.get_settings')
    @patch('honeypot.middleware.auth.get_settings')
    def setup_method(self, mock_auth_settings, mock_main_settings, mock_get_logger, mock_setup_logging):
        """Set up test fixtures."""
        # Mock settings for both main and auth middleware
        mock_settings = MagicMock()
        mock_settings.api_keys = ["test-api-key"]
        mock_auth_settings.return_value = mock_settings
        mock_main_settings.return_value = mock_settings
        
        # Mock logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        self.app = create_app()
        self.client = TestClient(self.app)
    
    def test_health_endpoint_no_auth(self):
        """Test health endpoint doesn't require authentication."""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "service": "agentic-honeypot"}
    
    def test_process_message_missing_auth(self):
        """Test process message endpoint requires authentication."""
        message_data = {
            "session_id": "test-session",
            "message": {
                "sender": "user",
                "text": "Hello",
                "timestamp": datetime.now().isoformat(),
                "message_id": "msg-1"
            },
            "conversation_history": [],
            "metadata": {
                "channel": "SMS",
                "language": "en",
                "locale": "en-US"
            }
        }
        
        response = self.client.post("/api/v1/process-message", json=message_data)
        assert response.status_code == 401
        assert response.json()["error_code"] == "MISSING_API_KEY"
    
    @patch('honeypot.middleware.auth.get_settings')
    def test_process_message_invalid_auth(self, mock_get_settings):
        """Test process message endpoint with invalid API key."""
        mock_settings = MagicMock()
        mock_settings.api_keys = ["valid-key"]
        mock_get_settings.return_value = mock_settings
        
        message_data = {
            "session_id": "test-session",
            "message": {
                "sender": "user",
                "text": "Hello",
                "timestamp": datetime.now().isoformat(),
                "message_id": "msg-1"
            },
            "conversation_history": [],
            "metadata": {
                "channel": "SMS",
                "language": "en",
                "locale": "en-US"
            }
        }
        
        headers = {"x-api-key": "invalid-key"}
        response = self.client.post("/api/v1/process-message", json=message_data, headers=headers)
        assert response.status_code == 401
        assert response.json()["error_code"] == "INVALID_API_KEY"
    
    @patch('honeypot.middleware.auth.get_settings')
    def test_process_message_valid_auth(self, mock_get_settings):
        """Test process message endpoint with valid API key."""
        mock_settings = MagicMock()
        mock_settings.api_keys = ["test-api-key"]
        mock_get_settings.return_value = mock_settings
        
        message_data = {
            "session_id": "test-session",
            "message": {
                "sender": "user",
                "text": "Hello",
                "timestamp": datetime.now().isoformat(),
                "message_id": "msg-1"
            },
            "conversation_history": [],
            "metadata": {
                "channel": "SMS",
                "language": "en",
                "locale": "en-US"
            }
        }
        
        headers = {"x-api-key": "test-api-key"}
        response = self.client.post("/api/v1/process-message", json=message_data, headers=headers)
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["status"] == "success"
        assert response_data["session_id"] == "test-session"
        assert "engagement_metrics" in response_data
        assert "extracted_intelligence" in response_data
    
    @patch('honeypot.middleware.auth.get_settings')
    def test_process_message_validation_error(self, mock_get_settings):
        """Test process message endpoint with invalid request data."""
        mock_settings = MagicMock()
        mock_settings.api_keys = ["test-api-key"]
        mock_get_settings.return_value = mock_settings
        
        # Missing required fields
        message_data = {
            "session_id": "",  # Empty session ID
            "message": {
                "sender": "user",
                "text": "",  # Empty text
                "timestamp": datetime.now().isoformat(),
                "message_id": "msg-1"
            },
            "metadata": {
                "channel": "SMS",
                "language": "en",
                "locale": "en-US"
            }
        }
        
        headers = {"x-api-key": "test-api-key"}
        response = self.client.post("/api/v1/process-message", json=message_data, headers=headers)
        assert response.status_code == 400
        assert "Session ID cannot be empty" in response.json()["detail"]