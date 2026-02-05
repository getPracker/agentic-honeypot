"""Application settings and configuration management."""

import os
import json
from typing import List, Optional
from functools import lru_cache

try:
    from pydantic import Field
    from pydantic_settings import BaseSettings, SettingsConfigDict
    PYDANTIC_AVAILABLE = True
except ImportError:
    # Fallback for environments where pydantic_settings isn't available
    PYDANTIC_AVAILABLE = False
    from pydantic import BaseModel, Field
    
    class BaseSettings(BaseModel):
        """Fallback BaseSettings implementation."""
        pass


if PYDANTIC_AVAILABLE:
    class Settings(BaseSettings):
        """Application settings loaded from environment variables."""
        
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False
        )
        
        # API Configuration
        api_host: str = Field(default="0.0.0.0")
        api_port: int = Field(default=8000)
        api_keys: List[str] = Field(default_factory=list)
        
        # Database Configuration
        database_url: str = Field(default="sqlite:///./honeypot.db")
        redis_url: str = Field(default="redis://localhost:6379/0")
        
        # LLM Configuration
        openai_api_key: Optional[str] = Field(None)
        gemini_api_key: Optional[str] = Field(None)
        anthropic_api_key: Optional[str] = Field(None)
        default_llm_provider: str = Field(default="openai")
        
        # Encryption Configuration
        encryption_key: str = Field(default="DGRP2s9PsfDib7V9rKaa4Dld-DfTaqPiCkIJ3Y1EOWQ=")
        
        # Callback Configuration
        guvi_callback_url: str = Field(
            default="https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
        )
        callback_timeout: int = Field(default=30)
        callback_max_retries: int = Field(default=3)
        
        # Logging Configuration
        log_level: str = Field(default="INFO")
        log_format: str = Field(default="json")
        
        # Performance Configuration
        max_concurrent_sessions: int = Field(default=100)
        session_timeout: int = Field(default=3600)
        response_timeout: int = Field(default=30)

else:
    class Settings:
        """Fallback settings implementation for environments without pydantic_settings."""
        
        def __init__(self):
            # API Configuration
            self.api_host = os.getenv("API_HOST", "0.0.0.0")
            self.api_port = int(os.getenv("API_PORT", "8000"))
            
            # Parse API_KEYS from JSON string or use default
            api_keys_str = os.getenv("API_KEYS", "[]")
            try:
                self.api_keys = json.loads(api_keys_str) if api_keys_str else []
            except json.JSONDecodeError:
                self.api_keys = []
            
            # Database Configuration
            self.database_url = os.getenv("DATABASE_URL", "sqlite:///./honeypot.db")
            self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            
            # LLM Configuration
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            self.gemini_api_key = os.getenv("GEMINI_API_KEY")
            self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
            self.default_llm_provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
            
            # Encryption Configuration
            self.encryption_key = os.getenv("ENCRYPTION_KEY", "DGRP2s9PsfDib7V9rKaa4Dld-DfTaqPiCkIJ3Y1EOWQ=")
            
            # Callback Configuration
            self.guvi_callback_url = os.getenv(
                "GUVI_CALLBACK_URL", 
                "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
            )
            self.callback_timeout = int(os.getenv("CALLBACK_TIMEOUT", "30"))
            self.callback_max_retries = int(os.getenv("CALLBACK_MAX_RETRIES", "3"))
            
            # Logging Configuration
            self.log_level = os.getenv("LOG_LEVEL", "INFO")
            self.log_format = os.getenv("LOG_FORMAT", "json")
            
            # Performance Configuration
            self.max_concurrent_sessions = int(os.getenv("MAX_CONCURRENT_SESSIONS", "100"))
            self.session_timeout = int(os.getenv("SESSION_TIMEOUT", "3600"))
            self.response_timeout = int(os.getenv("RESPONSE_TIMEOUT", "30"))


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()