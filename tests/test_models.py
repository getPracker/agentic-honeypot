"""Unit tests for data models."""

import pytest
from datetime import datetime
from hypothesis import given, strategies as st

from honeypot.models import (
    Message, MessageRequest, RequestMetadata, ScamAnalysis, ScamType,
    Session, SessionStatus, PersonaState, ScamIntelligence, BehaviorPatterns
)
from .conftest import (
    message_strategy, request_metadata_strategy, message_request_strategy,
    scam_analysis_strategy
)


class TestMessage:
    """Test cases for Message model."""
    
    def test_message_creation(self, sample_message):
        """Test basic message creation."""
        assert sample_message.sender == "user"
        assert sample_message.text == "Hello, I received your message about winning a lottery"
        assert isinstance(sample_message.timestamp, datetime)
        assert sample_message.message_id == "msg_001"
    
    @given(message_strategy())
    def test_message_properties(self, message):
        """Property test: Message should maintain all provided attributes."""
        assert hasattr(message, 'sender')
        assert hasattr(message, 'text')
        assert hasattr(message, 'timestamp')
        assert hasattr(message, 'message_id')
        assert isinstance(message.sender, str)
        assert isinstance(message.text, str)
        assert isinstance(message.timestamp, datetime)
        assert isinstance(message.message_id, str)


class TestRequestMetadata:
    """Test cases for RequestMetadata model."""
    
    def test_metadata_creation(self, sample_request_metadata):
        """Test basic metadata creation."""
        assert sample_request_metadata.channel == "SMS"
        assert sample_request_metadata.language == "en"
        assert sample_request_metadata.locale == "en-US"
        assert sample_request_metadata.source_ip == "192.168.1.1"
    
    @given(request_metadata_strategy())
    def test_metadata_validation(self, metadata):
        """Property test: RequestMetadata should validate all fields."""
        assert metadata.channel in ["SMS", "WhatsApp", "Email", "Telegram"]
        assert metadata.language in ["en", "hi", "es", "fr"]
        assert metadata.locale in ["en-US", "hi-IN", "es-ES", "fr-FR"]
        assert metadata.source_ip is None or isinstance(metadata.source_ip, str)


class TestMessageRequest:
    """Test cases for MessageRequest model."""
    
    def test_request_creation(self, sample_message_request):
        """Test basic request creation."""
        assert sample_message_request.session_id == "session_001"
        assert isinstance(sample_message_request.message, Message)
        assert sample_message_request.message.text == "Hello, I received your message about winning a lottery"
        assert isinstance(sample_message_request.conversation_history, list)
        assert isinstance(sample_message_request.metadata, RequestMetadata)
    
    @given(message_request_strategy())
    def test_request_structure(self, request):
        """Property test: MessageRequest should have valid structure."""
        assert isinstance(request.session_id, str)
        assert len(request.session_id) > 0
        assert isinstance(request.message, Message)
        assert len(request.message.text) > 0
        assert isinstance(request.conversation_history, list)
        assert isinstance(request.metadata, RequestMetadata)


class TestScamAnalysis:
    """Test cases for ScamAnalysis model."""
    
    def test_analysis_creation(self, sample_scam_analysis):
        """Test basic analysis creation."""
        assert sample_scam_analysis.is_scam is True
        assert sample_scam_analysis.confidence == 0.85
        assert sample_scam_analysis.scam_type == ScamType.FAKE_OFFER
        assert "lottery" in sample_scam_analysis.reasoning
        assert "lottery" in sample_scam_analysis.risk_indicators
    
    @given(scam_analysis_strategy())
    def test_analysis_properties(self, analysis):
        """Property test: ScamAnalysis should have valid properties."""
        assert isinstance(analysis.is_scam, bool)
        assert 0.0 <= analysis.confidence <= 1.0
        assert isinstance(analysis.scam_type, ScamType)
        assert isinstance(analysis.reasoning, str)
        assert len(analysis.reasoning) > 0
        assert isinstance(analysis.risk_indicators, list)


class TestSession:
    """Test cases for Session model."""
    
    def test_session_creation(self, sample_session):
        """Test basic session creation."""
        assert sample_session.session_id == "session_001"
        assert isinstance(sample_session.created_at, datetime)
        assert isinstance(sample_session.updated_at, datetime)
        assert sample_session.status == SessionStatus.ACTIVE
        assert len(sample_session.messages) == 0
        assert len(sample_session.scam_analyses) == 0
    
    def test_session_add_message(self, sample_session, sample_message):
        """Test adding messages to session."""
        initial_count = sample_session.get_message_count()
        sample_session.add_message(sample_message)
        assert sample_session.get_message_count() == initial_count + 1
        assert sample_message in sample_session.messages
    
    def test_session_add_analysis(self, sample_session, sample_scam_analysis):
        """Test adding analysis to session."""
        initial_count = len(sample_session.scam_analyses)
        sample_session.add_analysis(sample_scam_analysis)
        assert len(sample_session.scam_analyses) == initial_count + 1
        assert sample_scam_analysis in sample_session.scam_analyses


class TestPersonaState:
    """Test cases for PersonaState model."""
    
    def test_persona_creation(self, sample_persona_state):
        """Test basic persona creation."""
        assert sample_persona_state.persona_type == "curious_victim"
        assert "curious" in sample_persona_state.personality_traits
        assert sample_persona_state.trust_level == 0.7
        assert 0.0 <= sample_persona_state.trust_level <= 1.0
    
    def test_persona_initialization(self):
        """Test persona with None personality_traits."""
        persona = PersonaState(
            persona_type="test",
            personality_traits=None,
            background_story="test",
            current_mood="test",
            knowledge_level="test",
            trust_level=0.5
        )
        assert persona.personality_traits == []


class TestScamIntelligence:
    """Test cases for ScamIntelligence model."""
    
    def test_intelligence_initialization(self):
        """Test ScamIntelligence initialization with None values."""
        intelligence = ScamIntelligence(
            bank_accounts=None,
            upi_ids=None,
            phone_numbers=None,
            urls=None,
            keywords=None,
            behavior_patterns=None
        )
        
        assert intelligence.bank_accounts == []
        assert intelligence.upi_ids == []
        assert intelligence.phone_numbers == []
        assert intelligence.urls == []
        assert intelligence.keywords == []
        assert isinstance(intelligence.behavior_patterns, BehaviorPatterns)