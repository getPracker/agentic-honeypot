"""Application settings and configuration management."""

import os
from typing import List, Optional
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    database_url: str = Field(...)
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(None)
    anthropic_api_key: Optional[str] = Field(None)
    default_llm_provider: str = Field(default="openai")
    
    # Encryption Configuration
    encryption_key: str = Field(...)
    
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


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()