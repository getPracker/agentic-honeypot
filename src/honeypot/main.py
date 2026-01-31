"""Main application entry point."""

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import ValidationError
import re

from .config import get_settings
from .utils import setup_logging, get_logger
from .models.core import MessageRequest, MessageResponse, EngagementMetrics
from .middleware import AuthenticationMiddleware


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
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


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Set up logging first
    setup_logging()
    logger = get_logger(__name__)
    
    # Create FastAPI app
    app = FastAPI(
        title="Agentic Honey-Pot API",
        description="AI-powered scam detection and intelligence extraction system",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Get settings
    settings = get_settings()
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins if hasattr(settings, 'allowed_origins') else ["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )
    
    # Add trusted host middleware for production
    if hasattr(settings, 'trusted_hosts'):
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.trusted_hosts
        )
    
    # Add security headers middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        """Add security headers to all responses."""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response
    
    # Add authentication middleware
    app.add_middleware(AuthenticationMiddleware)
    
    # Add custom exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        logger.warning(f"Request validation error for {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": "Request validation failed",
                "error_code": "VALIDATION_ERROR",
                "details": exc.errors()
            }
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """Handle Pydantic validation errors."""
        logger.warning(f"Pydantic validation error for {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": "Data validation failed",
                "error_code": "DATA_VALIDATION_ERROR",
                "details": exc.errors()
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        logger.error(f"HTTP exception for {request.url.path}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.detail,
                "error_code": "HTTP_ERROR"
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception for {request.url.path}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Internal server error",
                "error_code": "INTERNAL_ERROR"
            }
        )
    
    # Initialize orchestrator
    from .services.orchestrator import MessageProcessor
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize resources on startup."""
        app.state.processor = MessageProcessor()
        logger.info("Message Processor Initialized")

    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "agentic-honeypot"}
    
    # Add message processing endpoint
    @app.post("/api/v1/process-message", response_model=MessageResponse)
    async def process_message(request: MessageRequest) -> MessageResponse:
        """
        Process incoming message for scam detection and intelligence extraction.
        
        This endpoint analyzes messages, detects scams, and generates appropriate responses.
        """
        logger.info(f"Processing message for session: {request.session_id}")
        
        # Sanitize inputs
        request.session_id = sanitize_input(request.session_id)
        request.message.text = sanitize_input(request.message.text)
        
        # Validate request data
        if not request.session_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session ID cannot be empty"
            )
        
        if not request.message.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message text cannot be empty"
            )
        
        # Additional validation: session ID format
        if not re.match(r'^[a-zA-Z0-9_-]{1,100}$', request.session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session ID format"
            )
        
        try:
            response = await app.state.processor.process_message(request)
            return response
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process message"
            )
    
    logger.info("Application created successfully")
    return app


def main() -> None:
    """Main entry point for running the application."""
    settings = get_settings()
    app = create_app()
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_config=None,  # Use our custom logging
    )


if __name__ == "__main__":
    main()