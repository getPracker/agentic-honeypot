"""Session management service."""

import logging
import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from ..config.settings import get_settings
from ..models.core import Message
from ..models.session import Session, SessionStatus


logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages conversation sessions with thread-safe operations.
    Currently implements in-memory storage.
    """

    def __init__(self):
        """Initialize the session manager."""
        self._settings = get_settings()
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.RLock()
        self._session_timeout = self._settings.session_timeout
        self._max_sessions = self._settings.max_concurrent_sessions

    def create_session(self, session_id: Optional[str] = None) -> Session:
        """
        Create a new session.

        Args:
            session_id: Optional custom session ID. If not provided, one will be generated.

        Returns:
            The created Session object.

        Raises:
            ValueError: If session_id already exists or max sessions reached.
        """
        if not session_id:
            session_id = str(uuid4())

        with self._lock:
            # Check maximum concurrent sessions (cleanup first)
            self._cleanup_expired_sessions()
            
            if len(self._sessions) >= self._max_sessions:
                logger.error("Maximum concurrent sessions limit reached")
                raise ValueError("Maximum concurrent sessions limit reached")

            if session_id in self._sessions:
                logger.warning(f"Session ID {session_id} already exists")
                raise ValueError(f"Session with ID {session_id} already exists")

            now = datetime.now(timezone.utc)
            session = Session(
                session_id=session_id,
                created_at=now,
                updated_at=now,
                status=SessionStatus.ACTIVE
            )
            self._sessions[session_id] = session
            logger.info(f"Created new session: {session_id}")
            return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieve a session by ID.

        Args:
            session_id: The ID of the session to retrieve.

        Returns:
            The Session object if found, else None.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return None
            
            # Check if expired
            if self._is_session_expired(session):
                logger.info(f"Session {session_id} expired during retrieval")
                # We optionally expire it here or just return None? 
                # Usually better to be explicit about expiry.
                # For now, let's treat it as found but maybe we should update status?
                # If we return it, the caller might try to use it.
                # Let's enforce expiry logic.
                self._terminate_session(session_id, SessionStatus.TERMINATED)
                 # Or maybe just return None if it's strictly timed out? 
                 # Task 2.5 mentions "lifecycle handling".
                return None
            
            return session

    def update_session(self, session: Session) -> None:
        """
        Update an existing session.

        Args:
            session: The session object with updated data.
        """
        with self._lock:
            if session.session_id not in self._sessions:
                raise ValueError(f"Session {session.session_id} not found")
            
            session.updated_at = datetime.now(timezone.utc)
            self._sessions[session.session_id] = session

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: The ID of the session to delete.

        Returns:
            True if deleted, False if not found.
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                logger.info(f"Deleted session: {session_id}")
                return True
            return False

    def list_active_sessions(self) -> List[Session]:
        """
        List all active sessions.

        Returns:
            List of active Session objects.
        """
        with self._lock:
            self._cleanup_expired_sessions()
            return [
                s for s in self._sessions.values() 
                if s.status == SessionStatus.ACTIVE
            ]

    def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions from storage."""
        # Note: This is called within other locked methods, so we don't need a lock here if strictly internal
        # But to be safe and consistent with the lock type (RLock), we can lock again.
        # However, modifying the dict while iterating is dangerous.
        
        expired_ids = []
        for session_id, session in self._sessions.items():
            if self._is_session_expired(session):
                expired_ids.append(session_id)
        
        for session_id in expired_ids:
            del self._sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")

    def _is_session_expired(self, session: Session) -> bool:
        """Check if a session has expired based on timeout."""
        if session.status != SessionStatus.ACTIVE:
            return False # Completed/Terminated sessions might stay for a bit or handled differently?
            # For in-memory limit, we probably want to clear them eventually. 
            # But let's assume 'expired' refers to timeout of active sessions.
        
        age = datetime.now(timezone.utc) - session.updated_at
        return age.total_seconds() > self._session_timeout

    def _terminate_session(self, session_id: str, status: SessionStatus) -> None:
        """Internal helper to mark session as terminated/completed."""
        if session_id in self._sessions:
            self._sessions[session_id].status = status
            self._sessions[session_id].updated_at = datetime.now(timezone.utc)

    def add_message_to_session(self, session_id: str, message: Message) -> Session:
        """
        Add a message to an active session.
        
        Args:
            session_id: The session ID.
            message: The message to add.
            
        Returns:
            The updated Session object.
            
        Raises:
            ValueError: If session not found or inactive.
        """
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found or expired")
            
            # Check for duplicates
            if any(m.message_id == message.message_id for m in session.messages):
                logger.warning(f"Message {message.message_id} already exists in session {session_id}")
                return session

            session.add_message(message)
            return session

    def validate_history(self, session_id: str, provided_history: List[Message]) -> bool:
        """
        Validate that provided history matches the stored session history.
        
        Args:
            session_id: The session ID.
            provided_history: The history provided in the request.
            
        Returns:
            True if valid, False otherwise.
        """
        with self._lock:
            session = self.get_session(session_id)
            if not session:
                # If session doesn't exist, we can't validate against it.
                # In the context of a new request creating a session, this might be called before creation?
                # Or if it's a new session, history should be empty? 
                # If session is missing, we consider validation failed if we expected one.
                return False

            if not provided_history:
                return True
            
            stored_msgs = session.messages
            
            # If provided history is longer than what we have, it's definitely wrong
            # (unless we missed messages, which implies sync issue)
            if len(provided_history) > len(stored_msgs):
                logger.warning(f"Provided history length ({len(provided_history)}) > stored ({len(stored_msgs)})")
                return False
            
            # Verify prefix match
            for i, msg in enumerate(provided_history):
                # Compare by ID and maybe content hash if needed, but ID is sufficient for now
                if msg.message_id != stored_msgs[i].message_id:
                    logger.warning(f"History mismatch at index {i}: provided {msg.message_id}, stored {stored_msgs[i].message_id}")
                    return False
            
            return True
