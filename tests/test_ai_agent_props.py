"""Property-based tests for AIAgent."""

import sys
import os
import unittest
from datetime import datetime

# Set required env vars for Settings
os.environ['DATABASE_URL'] = "sqlite:///test.db"
os.environ['ENCRYPTION_KEY'] = "test_key_12345"

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from hypothesis import given, strategies as st
from honeypot.services.ai_agent import AIAgent
from honeypot.models.session import Session, SessionStatus
from honeypot.models.scam import ScamAnalysis, ScamType

class TestAIAgentProperties(unittest.TestCase):
    def setUp(self):
        self.agent = AIAgent()
        self.agent.openai_client = None # Force mock mode for fast property tests

    @given(st.sampled_from(list(ScamType)))
    def test_persona_selection_completeness(self, scam_type):
        """Property: Agent handles all scam types for persona selection."""
        analysis = ScamAnalysis(
            is_scam=True,
            confidence=0.8,
            scam_type=scam_type,
            reasoning="test",
            risk_indicators=[]
        )
        persona = self.agent.select_persona(analysis)
        self.assertIsNotNone(persona)
        self.assertTrue(len(persona.persona_type) > 0)

    @given(st.text(min_size=1, max_size=100))
    def test_response_safety_invariant(self, message_text):
        """Property: Generated response is never unsafe (for mock generator)."""
        session = Session("id", datetime.utcnow(), datetime.utcnow(), SessionStatus.ACTIVE)
        response = self.agent.generate_response(session, message_text)
        
        # If response is generated, it must be safe
        if response:
            self.assertFalse(self.agent._is_unsafe_response(response))

if __name__ == '__main__':
    unittest.main()
