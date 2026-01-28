"""Unit tests for authentication middleware."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import Response

from honeypot.middleware.auth import AuthenticationMiddleware, create_auth_middleware


class TestAuthenticationMiddleware:
    """Test cases for authentication middleware."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = FastAPI()
        self.app.add_middleware(AuthenticationMiddleware)
        
        @self.app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        @self.app.get("/health")
        async def health_endpoint():
            return {"status": "healthy"}
        
        self.client = TestClient(self.app)
    
    @patch('honeypot.middleware.auth.get_settings')
    def test_excluded_paths_no_auth_required(self, mock_get_settings):
        """Test that excluded paths don't require authentication."""
        mock_settings = MagicMock()
        mock_settings.api_keys = ["valid-key"]
        mock_get_settings.return_value = mock_settings
        
        # Test health endpoint (excluded by default)
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    @patch('honeypot.middleware.auth.get_settings')
    def test_missing_api_key(self, mock_get_settings):
        """Test request without API key returns 401."""
        mock_settings = MagicMock()
        mock_settings.api_keys = ["valid-key"]
        mock_get_settings.return_value = mock_settings
        
        response = self.client.get("/test")
        assert response.status_code == 401
        assert response.json()["error_code"] == "MISSING_API_KEY"
    
    @patch('honeypot.middleware.auth.get_settings')
    def test_invalid_api_key(self, mock_get_settings):
        """Test request with invalid API key returns 401."""
        mock_settings = MagicMock()
        mock_settings.api_keys = ["valid-key"]
        mock_get_settings.return_value = mock_settings
        
        headers = {"x-api-key": "invalid-key"}
        response = self.client.get("/test", headers=headers)
        assert response.status_code == 401
        assert response.json()["error_code"] == "INVALID_API_KEY"
    
    @patch('honeypot.middleware.auth.get_settings')
    def test_valid_api_key(self, mock_get_settings):
        """Test request with valid API key succeeds."""
        mock_settings = MagicMock()
        mock_settings.api_keys = ["valid-key"]
        mock_get_settings.return_value = mock_settings
        
        headers = {"x-api-key": "valid-key"}
        response = self.client.get("/test", headers=headers)
        assert response.status_code == 200
        assert response.json() == {"message": "success"}
    
    @patch('honeypot.middleware.auth.get_settings')
    def test_create_auth_middleware(self, mock_get_settings):
        """Test middleware factory function."""
        mock_settings = MagicMock()
        mock_settings.api_keys = ["valid-key"]
        mock_get_settings.return_value = mock_settings
        
        app = FastAPI()
        middleware = create_auth_middleware(app, ["/custom-excluded"])
        
        assert isinstance(middleware, AuthenticationMiddleware)
        assert "/custom-excluded" in middleware.excluded_paths