"""Logging configuration and utilities."""

import re
import sys
import logging
from typing import Any, Dict, Optional
import structlog
from structlog.stdlib import LoggerFactory

from ..config import get_settings


def sanitize_log_data(data: Any) -> Any:
    """
    Sanitize sensitive data from log entries.
    
    Removes or redacts:
    - API keys
    - Phone numbers
    - Bank account numbers
    - Email addresses
    - URLs with sensitive parameters
    """
    if isinstance(data, str):
        # Redact API keys
        data = re.sub(r'(api[_-]?key["\s]*[:=]["\s]*)([^"\s,}]+)', r'\1***REDACTED***', data, flags=re.IGNORECASE)
        
        # Redact bank account numbers first (more specific pattern)
        data = re.sub(r'\b\d{12,18}\b', '***ACCOUNT***', data)
        
        # Redact phone numbers (basic pattern)
        data = re.sub(r'\b\d{10,11}\b', '***PHONE***', data)
        
        # Redact email addresses
        data = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***EMAIL***', data)
        
        # Redact URLs with sensitive parameters
        data = re.sub(r'(https?://[^\s]+[?&])(token|key|password|secret)=[^&\s]*', r'\1\2=***REDACTED***', data, flags=re.IGNORECASE)
        
    elif isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if key.lower() in ['api_key', 'password', 'secret', 'token', 'authorization']:
                sanitized[key] = '***REDACTED***'
            else:
                sanitized[key] = sanitize_log_data(value)
        return sanitized
        
    elif isinstance(data, list):
        return [sanitize_log_data(item) for item in data]
    
    return data


def setup_logging() -> None:
    """Set up structured logging configuration."""
    settings = get_settings()
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            sanitize_processor,
            structlog.processors.JSONRenderer() if settings.log_format == "json" 
            else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )


def sanitize_processor(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Structlog processor to sanitize sensitive data."""
    return sanitize_log_data(event_dict)


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """Get a configured logger instance."""
    return structlog.get_logger(name)