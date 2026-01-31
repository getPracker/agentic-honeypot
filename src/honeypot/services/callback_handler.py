"""Callback handler for external integrations."""

import logging
import json
from typing import Dict, Any, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

from ..config.settings import get_settings
from ..models.core import MessageResponse
from ..models.session import Session

logger = logging.getLogger(__name__)


class CallbackHandler:
    """
    Handles sending callback notifications to external systems.
    Includes retry logic and payload formatting.
    """

    def __init__(self):
        """Initialize the callback handler."""
        self._settings = get_settings()
        self._client = httpx.Client(timeout=self._settings.callback_timeout)
        self._callback_url = self._settings.guvi_callback_url
        self._max_retries = self._settings.callback_max_retries

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def send_callback(self, session: Session, response: MessageResponse) -> bool:
        """
        Send conversation results to the configured callback endpoint.
        
        Args:
            session: The completed session object.
            response: The final response object containing intelligence.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self._callback_url:
            logger.warning("No callback URL configured. Skipping.")
            return False

        payload = self._format_payload(session, response)
        
        try:
            logger.info(f"Sending callback to {self._callback_url} for session {session.session_id}")
            resp = self._client.post(self._callback_url, json=payload)
            resp.raise_for_status()
            logger.info(f"Callback successful: {resp.status_code}")
            return True
        except httpx.HTTPError as e:
            logger.error(f"Callback failed: {e}")
            raise # Trigger retry
        except Exception as e:
            logger.error(f"Unexpected error in callback: {e}")
            return False

    def _format_payload(self, session: Session, response: MessageResponse) -> Dict[str, Any]:
        """
        Format the callback payload according to requirements.
        
        Required fields:
        - sessionId
        - scamDetected
        - totalMessagesExchanged
        - extractedIntelligence
        - agentNotes
        """
        # Convert Pydantic models to dict if needed, or construct manually
        # extracted_intelligence is already a dict in MessageResponse based on current def, 
        # or it might be the object which needs dump. 
        # In MessageResponse model it is defined as dict. 
        # In Session model it is Optional[ScamIntelligence].
        # We should prefer the rich object from Session if available and serialize it.
        
        intelligence = {}
        if session.extracted_intelligence:
            # We can use a utility to dump dataclass/pydantic to dict
            # Since ScamIntelligence is a dataclass (from our current code), we can use asdict or manual
            from dataclasses import asdict
            intelligence = asdict(session.extracted_intelligence)
        elif isinstance(response.extracted_intelligence, dict):
            intelligence = response.extracted_intelligence

        return {
            "sessionId": session.session_id,
            "scamDetected": response.scam_detected,
            "totalMessagesExchanged": session.get_message_count(),
            "extractedIntelligence": intelligence,
            "agentNotes": session.agent_notes or response.agent_notes
        }

    def close(self):
        """Close the HTTP client."""
        self._client.close()
