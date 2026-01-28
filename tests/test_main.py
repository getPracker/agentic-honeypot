"""Unit tests for main application."""

import pytest
from unittest.mock import patch, MagicMock

from honeypot.main import create_app


class TestMainApplication:
    """Test cases for main application."""
    
    @patch('honeypot.main.setup_logging')
    @patch('honeypot.main.get_logger')
    def test_create_app(self, mock_get_logger, mock_setup_logging):
        """Test application creation."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        app = create_app()
        
        # Verify logging setup was called
        mock_setup_logging.assert_called_once()
        mock_get_logger.assert_called_once()
        
        # Verify app properties
        assert app.title == "Agentic Honey-Pot API"
        assert app.version == "0.1.0"
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"
        
        # Verify logger was called
        mock_logger.info.assert_called_once_with("Application created successfully")