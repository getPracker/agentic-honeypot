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
        Format the callback payload according to GUVI requirements.
        
        GUVI Required format:
        {
            "sessionId": "abc123-session-id",
            "scamDetected": true,
            "totalMessagesExchanged": 18,
            "extractedIntelligence": {
                "bankAccounts": ["XXXX-XXXX-XXXX"],
                "upiIds": ["scammer@upi"],
                "phishingLinks": ["http://malicious-link.example"],
                "phoneNumbers": ["+91XXXXXXXXXX"],
                "suspiciousKeywords": ["urgent", "verify now", "account blocked"]
            },
            "agentNotes": "Scammer used urgency tactics and payment redirection"
        }
        """
        
        # Initialize intelligence with GUVI format
        intelligence = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }
        
        # Extract intelligence from session if available
        if session.extracted_intelligence:
            intel = session.extracted_intelligence
            
            # Convert bank accounts
            if intel.bank_accounts:
                intelligence["bankAccounts"] = [
                    acc.account_number for acc in intel.bank_accounts
                ]
            
            # Convert UPI IDs
            if intel.upi_ids:
                intelligence["upiIds"] = intel.upi_ids
            
            # Convert URLs to phishing links
            if intel.urls:
                intelligence["phishingLinks"] = [
                    url.url for url in intel.urls
                ]
            
            # Convert phone numbers
            if intel.phone_numbers:
                intelligence["phoneNumbers"] = [
                    phone.number for phone in intel.phone_numbers
                ]
            
            # Convert keywords to suspicious keywords
            if intel.keywords:
                intelligence["suspiciousKeywords"] = intel.keywords
        
        # Fallback to response intelligence if session doesn't have it
        elif isinstance(response.extracted_intelligence, dict):
            resp_intel = response.extracted_intelligence
            
            # Map from response format to GUVI format
            intelligence["bankAccounts"] = self._extract_bank_accounts(resp_intel)
            intelligence["upiIds"] = resp_intel.get("upi_ids", [])
            intelligence["phishingLinks"] = self._extract_urls(resp_intel)
            intelligence["phoneNumbers"] = self._extract_phone_numbers(resp_intel)
            intelligence["suspiciousKeywords"] = resp_intel.get("keywords", [])

        return {
            "sessionId": session.session_id,
            "scamDetected": response.scam_detected,
            "totalMessagesExchanged": session.get_message_count(),
            "extractedIntelligence": intelligence,
            "agentNotes": session.agent_notes or response.agent_notes or "AI agent engagement completed"
        }
    
    def _extract_bank_accounts(self, intelligence_dict: dict) -> List[str]:
        """Extract bank account numbers from intelligence dict."""
        bank_accounts = intelligence_dict.get("bank_accounts", [])
        if isinstance(bank_accounts, list):
            # Handle both string format and dict format
            return [
                acc if isinstance(acc, str) else acc.get("account_number", "")
                for acc in bank_accounts
                if acc
            ]
        return []
    
    def _extract_phone_numbers(self, intelligence_dict: dict) -> List[str]:
        """Extract phone numbers from intelligence dict."""
        phone_numbers = intelligence_dict.get("phone_numbers", [])
        if isinstance(phone_numbers, list):
            # Handle both string format and dict format
            return [
                phone if isinstance(phone, str) else phone.get("number", "")
                for phone in phone_numbers
                if phone
            ]
        return []
    
    def _extract_urls(self, intelligence_dict: dict) -> List[str]:
        """Extract URLs from intelligence dict."""
        urls = intelligence_dict.get("urls", [])
        if isinstance(urls, list):
            # Handle both string format and dict format
            return [
                url if isinstance(url, str) else url.get("url", "")
                for url in urls
                if url
            ]
        return []

    def close(self):
        """Close the HTTP client."""
        self._client.close()
