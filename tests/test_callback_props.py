"""Property tests for CallbackHandler."""

import sys
import os
import unittest
from hypothesis import given, strategies as st
from unittest.mock import MagicMock, patch

# Set required env vars
os.environ['DATABASE_URL'] = "sqlite:///test.db"
os.environ['ENCRYPTION_KEY'] = "test_key_12345"
os.environ['API_KEYS'] = '["test"]'

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeypot.services.callback_handler import CallbackHandler
from honeypot.models.session import Session, SessionStatus
from honeypot.models.core import MessageResponse, EngagementMetrics, Message
from datetime import datetime

class TestCallbackHandlerProperties(unittest.TestCase):
    def setUp(self):
        self.handler = CallbackHandler()

    @given(st.text(), st.booleans())
    def test_payload_completeness(self, text_input, is_scam):
        """Property: Payload always contains required fields."""
        # Create minimal objects
        # We need valid date times for session
        now = datetime.utcnow()
        session = Session("id", now, now, SessionStatus.COMPLETED)
        metrics = EngagementMetrics(conversation_duration=0, message_count=0, engagement_quality=0.0, intelligence_score=0.0)
        response = MessageResponse(status="ok", scam_detected=is_scam, engagement_metrics=metrics, session_id="id")
        
        # Test private method _format_payload directly to verify structure without networking
        payload = self.handler._format_payload(session, response)
        
        required_fields = ["sessionId", "scamDetected", "totalMessagesExchanged", "extractedIntelligence", "agentNotes"]
        for field in required_fields:
            self.assertIn(field, payload)

if __name__ == '__main__':
    unittest.main()
