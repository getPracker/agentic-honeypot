"""Main application entry point."""

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from .config import get_settings
from .utils import setup_logging, get_logger
from .models.core import MessageRequest, MessageResponse, EngagementMetrics
from .middleware import AuthenticationMiddleware


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
        
        # TODO: This is a placeholder implementation
        # The actual processing logic will be implemented in later tasks
        return MessageResponse(
            status="success",
            scam_detected=False,
            agent_response=None,
            engagement_metrics=EngagementMetrics(
                conversation_duration=0,
                message_count=1,
                engagement_quality=0.0,
                intelligence_score=0.0
            ),
            extracted_intelligence={},
            agent_notes="Message processed successfully",
            session_id=request.session_id
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