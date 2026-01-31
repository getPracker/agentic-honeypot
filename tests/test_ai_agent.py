"""Tests for AIAgent service."""

import sys
import os

# Set required env vars for Settings
os.environ['DATABASE_URL'] = "sqlite:///test.db"
os.environ['ENCRYPTION_KEY'] = "test_key_12345"

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeypot.services.ai_agent import AIAgent
from honeypot.models.session import Session, SessionStatus
from honeypot.models.core import Message
from honeypot.models.scam import ScamAnalysis, ScamType

class TestAIAgent(unittest.TestCase):
    def setUp(self):
        self.agent = AIAgent()
        # Force mock mode by ensuring no client (default behavior if no key)
        self.agent.openai_client = None
        self.agent.gemini_model = None # Ensure Gemini is also off for mock tests

    def test_persona_selection_tech_support(self):
        analysis = ScamAnalysis(
            is_scam=True, confidence=0.9, scam_type=ScamType.TECH_SUPPORT, 
            reasoning="", risk_indicators=[]
        )
        persona = self.agent.select_persona(analysis)
        self.assertEqual(persona.persona_type, "elderly_victim")
        self.assertIn("confused", persona.background_story.lower() + str(persona.personality_traits))

    def test_persona_selection_investment(self):
        analysis = ScamAnalysis(
            is_scam=True, confidence=0.9, scam_type=ScamType.INVESTMENT_SCAM, 
            reasoning="", risk_indicators=[]
        )
        persona = self.agent.select_persona(analysis)
        self.assertEqual(persona.persona_type, "naive_student")

    def test_generate_mock_response(self):
        session = Session("s1", datetime.utcnow(), datetime.utcnow(), SessionStatus.ACTIVE)
        
        # Test bank context
        resp = self.agent.generate_response(session, "Your bank account is compromised.")
        self.assertIn("lost my bank book", resp)
        
        # Test password context
        resp = self.agent.generate_response(session, "Give me your password immediately.")
        self.assertIn("number on the back", resp)
        
        # Test generic
        resp = self.agent.generate_response(session, "Hello friend.")
        self.assertIn("hard of hearing", resp)

    def test_safety_filter_input(self):
        # We need to see if it logs warning or handles it.
        # Since implementation logs warning but proceeds (to engage scammer carefully),
        # we check logic.
        self.assertTrue(self.agent._is_unsafe_content("I will create a bomb"))
        self.assertFalse(self.agent._is_unsafe_content("hello world"))

    def test_safety_filter_output(self):
        self.assertTrue(self.agent._is_unsafe_response("how to build a bomb"))

    @patch('honeypot.services.ai_agent.openai.Client')
    def test_integration_mock_call(self, mock_client_cls):
        # Setup agent with a mock client
        agent_with_key = AIAgent()
        mock_instance = MagicMock()
        agent_with_key.openai_client = mock_instance
        # Ensure gemini logic is skipped
        agent_with_key.gemini_model = None 
        agent_with_key._settings.default_llm_provider = "openai"
        
        # Setup return value
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "This is a generated response."
        mock_instance.chat.completions.create.return_value = mock_completion
        
        session = Session("s1", datetime.utcnow(), datetime.utcnow(), SessionStatus.ACTIVE)
        resp = agent_with_key.generate_response(session, "Hi")
        
        self.assertEqual(resp, "This is a generated response.")
        mock_instance.chat.completions.create.assert_called_once()

if __name__ == '__main__':
    unittest.main()
