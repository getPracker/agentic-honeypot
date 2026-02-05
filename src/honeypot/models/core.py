"""Core data models for message processing and API interactions."""

from datetime import datetime
from typing import List, Optional, Union
from dataclasses import dataclass
from pydantic import BaseModel, Field, validator, root_validator


class Message(BaseModel):
    """Represents a single message in a conversation."""
    sender: str = Field(..., description="Message sender identifier")
    text: str = Field(..., description="Message content")
    timestamp: Union[datetime, int, str] = Field(..., description="Message timestamp")
    message_id: Optional[str] = Field(None, description="Unique message identifier")
    
    @root_validator(pre=True)
    def handle_message_aliases(cls, values):
        """Handle both camelCase and snake_case field names."""
        # Handle messageId -> message_id
        if 'messageId' in values and 'message_id' not in values:
            values['message_id'] = values.pop('messageId')
        return values
    
    @validator('timestamp', pre=True)
    def parse_timestamp(cls, v):
        """Parse timestamp from various formats."""
        if isinstance(v, int):
            # Unix timestamp in milliseconds
            if v > 1e10:  # Likely milliseconds
                return datetime.fromtimestamp(v / 1000)
            else:  # Likely seconds
                return datetime.fromtimestamp(v)
        elif isinstance(v, str):
            # ISO format string
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except:
                return datetime.now()
        return v
    
    @validator('message_id', pre=True, always=True)
    def generate_message_id(cls, v):
        """Generate message_id if not provided."""
        if v is None:
            import uuid
            return f"msg_{uuid.uuid4().hex[:8]}"
        return v
    
    class Config:
        allow_population_by_field_name = True


class RequestMetadata(BaseModel):
    """Metadata associated with an incoming request."""
    channel: str = Field(..., description="Communication channel (SMS, WhatsApp, Email)")
    language: str = Field(..., description="Language code (e.g., 'en', 'hi')")
    locale: str = Field(..., description="Locale code (e.g., 'en-US', 'hi-IN')")
    source_ip: Optional[str] = Field(None, description="Source IP address")
    
    @root_validator(pre=True)
    def handle_metadata_aliases(cls, values):
        """Handle both camelCase and snake_case field names."""
        # Handle sourceIp -> source_ip
        if 'sourceIp' in values and 'source_ip' not in values:
            values['source_ip'] = values.pop('sourceIp')
        return values
    
    @validator('language', pre=True)
    def normalize_language(cls, v):
        """Normalize language codes."""
        if v.lower() == 'english':
            return 'en'
        return v.lower()
    
    @validator('locale', pre=True)
    def normalize_locale(cls, v):
        """Normalize locale codes."""
        if v == 'IN':
            return 'en-IN'
        return v
    
    class Config:
        allow_population_by_field_name = True


class MessageRequest(BaseModel):
    """Request model for incoming messages."""
    session_id: str = Field(..., description="Unique session identifier")
    message: Message = Field(..., description="Message object")
    conversation_history: List[Message] = Field(default_factory=list, description="Previous messages")
    metadata: RequestMetadata = Field(..., description="Request metadata")
    
    @root_validator(pre=True)
    def handle_field_aliases(cls, values):
        """Handle both camelCase and snake_case field names."""
        # Handle sessionId -> session_id
        if 'sessionId' in values and 'session_id' not in values:
            values['session_id'] = values.pop('sessionId')
        
        # Handle conversationHistory -> conversation_history
        if 'conversationHistory' in values and 'conversation_history' not in values:
            values['conversation_history'] = values.pop('conversationHistory')
        
        return values
    
    class Config:
        allow_population_by_field_name = True


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