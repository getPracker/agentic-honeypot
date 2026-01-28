"""Tests for CallbackHandler service."""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Set required env vars
os.environ['DATABASE_URL'] = "sqlite:///test.db"
os.environ['ENCRYPTION_KEY'] = "test_key_12345"

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeypot.services.callback_handler import CallbackHandler
from honeypot.models.session import Session, SessionStatus
from honeypot.models.core import MessageResponse, EngagementMetrics

class TestCallbackHandler(unittest.TestCase):
    def setUp(self):
        self.handler = CallbackHandler()

    @patch('honeypot.services.callback_handler.httpx.Client.post')
    def test_send_callback_success(self, mock_post):
        # Setup mock success
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Data
        session = Session("s1", datetime.utcnow(), datetime.utcnow(), SessionStatus.COMPLETED)
        metrics = EngagementMetrics(conversation_duration=10, message_count=2, engagement_quality=1.0, intelligence_score=0.5)
        response = MessageResponse(
            status="success", scam_detected=True, agent_response="bye", 
            engagement_metrics=metrics, extracted_intelligence={}, agent_notes="note", session_id="s1"
        )

        result = self.handler.send_callback(session, response)
        
        self.assertTrue(result)
        mock_post.assert_called_once()
        
        # Verify payload structure
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        self.assertEqual(payload['sessionId'], "s1")
        self.assertEqual(payload['scamDetected'], True)
        self.assertEqual(payload['totalMessagesExchanged'], 0) # Session empty in test
        self.assertEqual(payload['agentNotes'], "note")

    @patch('honeypot.services.callback_handler.httpx.Client.post')
    def test_send_callback_failure_retry(self, mock_post):
        # Setup failure
        import httpx
        mock_post.side_effect = [
            httpx.ConnectError("Fail 1"),
            httpx.ConnectError("Fail 2"),
            MagicMock(status_code=200, raise_for_status=lambda: None) # Success on 3rd
        ]

        session = Session("s1", datetime.utcnow(), datetime.utcnow(), SessionStatus.COMPLETED)
        # We need simpler response obj
        metrics = EngagementMetrics(conversation_duration=0, message_count=0, engagement_quality=0, intelligence_score=0)
        response = MessageResponse(
            status="ok", scam_detected=False, agent_response="", 
            engagement_metrics=metrics, session_id="s1"
        )
        
        # We need to reduce retry wait for test speed?
        # Tenacity wait_exponential can be slow. 
        # But we mocked the post, it's the logic we test.
        # Let's hope it runs fast enough or we mock time.sleep equivalent?
        # Tenacity runs logic itself.
        
        # Alternatively, we rely on tenacity default behavior for tests (it waits). 
        # To make it fast, we can mock time.sleep or reconfigure tenacity for tests?
        # Or just assert it fails if we mock constant failure.
        
        # Let's try constant failure to see exception raised after retries
        mock_post.side_effect = httpx.ConnectError("Always Fail")
        
        with self.assertRaises(Exception): # tenacity raises RetryError wrapping original
             self.handler.send_callback(session, response)
        
        self.assertEqual(mock_post.call_count, 3) # Stopped after 3 attempts

if __name__ == '__main__':
    unittest.main()
