"""Core data models for message processing and API interactions."""

from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents a single message in a conversation."""
    sender: str = Field(..., description="Message sender identifier")
    text: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")
    message_id: str = Field(..., description="Unique message identifier")


class RequestMetadata(BaseModel):
    """Metadata associated with an incoming request."""
    channel: str = Field(..., description="Communication channel (SMS, WhatsApp, Email)")
    language: str = Field(..., description="Language code (e.g., 'en', 'hi')")
    locale: str = Field(..., description="Locale code (e.g., 'en-US', 'hi-IN')")
    source_ip: Optional[str] = Field(None, description="Source IP address")


class MessageRequest(BaseModel):
    """Request model for incoming messages."""
    session_id: str = Field(..., description="Unique session identifier")
    message: Message = Field(..., description="Message object")
    conversation_history: List[Message] = Field(default_factory=list, description="Previous messages")
    metadata: RequestMetadata = Field(..., description="Request metadata")


class EngagementMetrics(BaseModel):
    """Metrics about conversation engagement."""
    conversation_duration: int = Field(..., description="Conversation duration in seconds")
    message_count: int = Field(..., description="Total number of messages")
    engagement_quality: float = Field(..., description="Engagement quality score (0.0 to 1.0)")
    intelligence_score: float = Field(..., description="Intelligence extraction score (0.0 to 1.0)")


class MessageResponse(BaseModel):
    """Response model for processed messages."""
    status: str = Field(..., description="Response status (success/error)")
    scam_detected: bool = Field(..., description="Whether scam was detected")
    agent_response: Optional[str] = Field(None, description="AI agent response")
    engagement_metrics: EngagementMetrics = Field(..., description="Engagement metrics")
    extracted_intelligence: dict = Field(default_factory=dict, description="Extracted intelligence")
    agent_notes: str = Field("", description="Agent notes about the conversation")
    session_id: str = Field(..., description="Session identifier")