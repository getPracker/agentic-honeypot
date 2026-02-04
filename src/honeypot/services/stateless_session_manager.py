"""Stateless session management service for serverless deployment."""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from ..models.core import Message
from ..models.session import Session, SessionStatus
from ..models.scam import ScamAnalysis

logger = logging.getLogger(__name__)


class StatelessSessionManager:
    """
    Stateless session manager that reconstructs sessions from conversation history.
    Perfect for serverless environments where state is not persisted between requests.
    """

    def create_session_from_history(
        self, 
        session_id: str, 
        conversation_history: List[Message],
        current_message: Message
    ) -> Session:
        """
        Create a session object from conversation history and current message.
        
        Args:
            session_id: The session identifier
            conversation_history: List of previous Message objects
            current_message: The current incoming message
            
        Returns:
            A reconstructed Session object
        """
        now = datetime.now(timezone.utc)
        
        # Create base session
        session = Session(
            session_id=session_id,
            created_at=now,
            updated_at=now,
            status=SessionStatus.ACTIVE
        )
        
        # Add conversation history messages (already Message objects)
        for message in conversation_history:
            session.add_message(message)
        
        # Add current message
        session.add_message(current_message)
        
        total_messages = len(conversation_history) + 1
        logger.info(f"Reconstructed session {session_id} with {total_messages} messages")
        return session
    
    def _parse_timestamp(self, timestamp_data) -> datetime:
        """Parse timestamp from various formats."""
        if isinstance(timestamp_data, (int, float)):
            # Assume Unix timestamp in milliseconds
            return datetime.fromtimestamp(timestamp_data / 1000, tz=timezone.utc)
        elif isinstance(timestamp_data, str):
            try:
                # Try ISO format
                return datetime.fromisoformat(timestamp_data.replace('Z', '+00:00'))
            except ValueError:
                pass
        
        # Fallback to current time
        return datetime.now(timezone.utc)
    
    def add_analysis_to_session(self, session: Session, analysis: ScamAnalysis) -> None:
        """Add scam analysis to session."""
        session.add_analysis(analysis)
    
    def validate_history_format(self, conversation_history: List[Message]) -> bool:
        """
        Validate that conversation history has the expected format.
        
        Args:
            conversation_history: List of Message objects
            
        Returns:
            True if format is valid
        """
        if not isinstance(conversation_history, list):
            return False
        
        for msg in conversation_history:
            if not isinstance(msg, Message):
                return False
            
            # Check required fields exist (Pydantic should ensure this)
            if not msg.text:
                return False
        
        return True
    
    def get_conversation_summary(self, session: Session) -> dict:
        """
        Get a summary of the conversation for logging/callback purposes.
        
        Args:
            session: The session object
            
        Returns:
            Dictionary with conversation summary
        """
        return {
            "session_id": session.session_id,
            "message_count": len(session.messages),
            "duration_seconds": session.get_conversation_duration(),
            "scam_analyses_count": len(session.scam_analyses),
            "has_intelligence": bool(session.extracted_intelligence),
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }