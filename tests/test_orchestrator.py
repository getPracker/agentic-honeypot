"""Tests for MessageProcessor orchestration."""

import sys
import os
import unittest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime

# Set required env vars
os.environ['DATABASE_URL'] = "sqlite:///test.db"
os.environ['ENCRYPTION_KEY'] = "test_key_12345"
os.environ['API_KEYS'] = '["test"]'

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeypot.services.orchestrator import MessageProcessor
from honeypot.models.core import Message, MessageRequest, RequestMetadata
from honeypot.models.scam import ScamAnalysis, ScamType

class TestMessageProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = MessageProcessor()
        # Mock external dependencies to isolate orchestration logic
        self.processor.ai_agent = MagicMock()
        self.processor.callback_handler = MagicMock()
        
        # Configure simple defaults
        self.processor.ai_agent.generate_response.return_value = None

    def test_process_new_clean_message(self):
        # Setup
        msg = Message(sender="user", text="hello", timestamp=datetime.utcnow(), message_id="m1")
        req = MessageRequest(
            session_id="new_sess", 
            message=msg, 
            conversation_history=[],
            metadata=RequestMetadata(channel="sms", language="en", locale="en", source_ip="")
        )
        
        # Execute
        response = asyncio.run(self.processor.process_message(req))
        
        # Verify
        self.assertEqual(response.session_id, "new_sess")
        self.assertFalse(response.scam_detected)
        self.assertIsNone(response.agent_response)
        
        # Verify session state
        session = self.processor.session_manager.get_session("new_sess")
        self.assertIsNotNone(session)
        self.assertEqual(len(session.messages), 1)

    def test_process_scam_message_engages_agent(self):
        # Setup
        msg = Message(sender="user", text="winner lottery prize", timestamp=datetime.utcnow(), message_id="m2")
        req = MessageRequest(
            session_id="scam_sess", 
            message=msg, 
            conversation_history=[],
            metadata=RequestMetadata(channel="sms", language="en", locale="en", source_ip="")
        )
        
        # Mock agent response
        self.processor.ai_agent.generate_response.return_value = "Agent reply"
        
        # Execute
        response = asyncio.run(self.processor.process_message(req))
        
        # Verify
        self.assertTrue(response.scam_detected)
        self.assertEqual(response.agent_response, "Agent reply")
        
        # Verify interactions
        self.processor.ai_agent.generate_response.assert_called_once()
        self.processor.callback_handler.send_callback.assert_called_once() # Should callback on scam
        
        # Verify session has both messages
        session = self.processor.session_manager.get_session("scam_sess")
        self.assertEqual(len(session.messages), 2) # User + Agent

    def test_intelligence_aggregation(self):
        # Setup session with partial intel
        # We simulate a flow where we send one msg with parsing info
        msg = Message(sender="user", text="my account is 1234567890", timestamp=datetime.utcnow(), message_id="m3")
        req = MessageRequest(
            session_id="intel_sess", 
            message=msg, 
            conversation_history=[],
            metadata=RequestMetadata(channel="sms", language="en", locale="en", source_ip="")
        )
        
        # Execute
        response = asyncio.run(self.processor.process_message(req))
        
        # Verify extracted
        self.assertIn("bank_accounts", response.extracted_intelligence)
        self.assertEqual(len(response.extracted_intelligence['bank_accounts']), 1)
        self.assertEqual(response.extracted_intelligence['bank_accounts'][0]['account_number'], "1234567890")

if __name__ == '__main__':
    unittest.main()
