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
        conversation_history: List[dict],
        current_message: Message
    ) -> Session:
        """
        Create a session object from conversation history and current message.
        
        Args:
            session_id: The session identifier
            conversation_history: List of previous messages in dict format
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
        
        # Convert conversation history to Message objects
        messages = []
        for i, msg_data in enumerate(conversation_history):
            message = Message(
                sender=msg_data.get("sender", "unknown"),
                text=msg_data.get("text", ""),
                timestamp=self._parse_timestamp(msg_data.get("timestamp")),
                message_id=msg_data.get("message_id", f"hist_{i}")
            )
            messages.append(message)
        
        # Add current message
        messages.append(current_message)
        
        # Add all messages to session
        for message in messages:
            session.add_message(message)
        
        logger.info(f"Reconstructed session {session_id} with {len(messages)} messages")
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
    
    def validate_history_format(self, conversation_history: List[dict]) -> bool:
        """
        Validate that conversation history has the expected format.
        
        Args:
            conversation_history: List of message dictionaries
            
        Returns:
            True if format is valid
        """
        if not isinstance(conversation_history, list):
            return False
        
        for msg in conversation_history:
            if not isinstance(msg, dict):
                return False
            
            # Check required fields
            if "text" not in msg:
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