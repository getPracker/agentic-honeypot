"""End-to-end property tests for message flow."""

import sys
import os
import unittest
import asyncio
from unittest.mock import MagicMock, patch
from hypothesis import given, strategies as st

# Set required env vars
os.environ['DATABASE_URL'] = "sqlite:///test.db"
os.environ['ENCRYPTION_KEY'] = "test_key_12345"
os.environ['API_KEYS'] = '["test"]'

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeypot.services.orchestrator import MessageProcessor
from honeypot.models.core import Message, MessageRequest, RequestMetadata
from datetime import datetime

class TestEndToEndProperties(unittest.TestCase):
    def setUp(self):
        # We need to mock callback handler heavily to avoid network
        with patch('honeypot.services.callback_handler.CallbackHandler.__init__', return_value=None):
            self.processor = MessageProcessor()
            # Force mock components where needed
            self.processor.callback_handler = MagicMock()
            # Agent can stay in mock mode (no keys configured in test env)

    @given(st.text(min_size=1, max_size=100))
    def test_flow_stability(self, msg_text):
        """Property: Pipeline processes any non-empty text without crashing."""
        msg = Message(sender="user", text=msg_text, timestamp=datetime.utcnow(), message_id="p1")
        req = MessageRequest(
            session_id="prop_sess", 
            message=msg, 
            conversation_history=[],
            metadata=RequestMetadata(channel="sms", language="en", locale="en", source_ip="")
        )
        
        # We run async in sync test wrapper
        # Using loop is tricky in hypothesis, but simple run should work if careful
        try:
             response = asyncio.run(self.processor.process_message(req))
             self.assertIsNotNone(response.session_id)
        except RuntimeError:
             # Handle nested loop issues if hypothesis does weird stuff, but usually fine for simple check
             # Or just create new loop
             loop = asyncio.new_event_loop()
             asyncio.set_event_loop(loop)
             response = loop.run_until_complete(self.processor.process_message(req))
             loop.close()
             self.assertIsNotNone(response.session_id)

if __name__ == '__main__':
    unittest.main()
