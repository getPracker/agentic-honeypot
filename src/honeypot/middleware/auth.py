"""Authentication middleware for API key validation."""

from typing import Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import get_settings
from ..utils import get_logger

logger = get_logger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to handle API key authentication."""
    
    def __init__(self, app, excluded_paths: list = None):
        """
        Initialize authentication middleware.
        
        Args:
            app: FastAPI application instance
            excluded_paths: List of paths to exclude from authentication
        """
        super().__init__(app)
        self.excluded_paths = excluded_paths or ["/health", "/docs", "/redoc", "/openapi.json"]
        self.settings = get_settings()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and validate API key authentication.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in the chain
            
        Returns:
            HTTP response
        """
        # Skip authentication for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        # Extract API key from header
        api_key = request.headers.get("x-api-key")
        
        # Check if API key is provided
        if not api_key:
            logger.warning(f"Missing API key for request to {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": "error",
                    "message": "Missing x-api-key header",
                    "error_code": "MISSING_API_KEY"
                }
            )
        
        # Validate API key
        if not self._is_valid_api_key(api_key):
            logger.warning(f"Invalid API key for request to {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": "error",
                    "message": "Invalid API key",
                    "error_code": "INVALID_API_KEY"
                }
            )
        
        # API key is valid, proceed with request
        logger.debug(f"Valid API key provided for {request.url.path}")
        return await call_next(request)
    
    def _is_valid_api_key(self, api_key: str) -> bool:
        """
        Validate the provided API key.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if API key is valid, False otherwise
        """
        return api_key in self.settings.api_keys


def create_auth_middleware(app, excluded_paths: list = None) -> AuthenticationMiddleware:
    """
    Create and configure authentication middleware.
    
    Args:
        app: FastAPI application instance
        excluded_paths: List of paths to exclude from authentication
        
    Returns:
        Configured authentication middleware
    """
    return AuthenticationMiddleware(app, excluded_paths)