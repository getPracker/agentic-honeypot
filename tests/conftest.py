"""Pytest configuration and shared fixtures."""

import pytest
from datetime import datetime
from typing import List
from hypothesis import strategies as st

from honeypot.models import (
    Message, MessageRequest, RequestMetadata, ScamAnalysis, ScamType,
    Session, SessionStatus, PersonaState, EngagementStrategy, ConversationStage
)


@pytest.fixture
def sample_message() -> Message:
    """Create a sample message for testing."""
    return Message(
        sender="user",
        text="Hello, I received your message about winning a lottery",
        timestamp=datetime.utcnow(),
        message_id="msg_001"
    )


@pytest.fixture
def sample_request_metadata() -> RequestMetadata:
    """Create sample request metadata."""
    return RequestMetadata(
        channel="SMS",
        language="en",
        locale="en-US",
        source_ip="192.168.1.1"
    )


@pytest.fixture
def sample_message_request(sample_request_metadata: RequestMetadata, sample_message: Message) -> MessageRequest:
    """Create a sample message request."""
    return MessageRequest(
        session_id="session_001",
        message=sample_message,
        conversation_history=[],
        metadata=sample_request_metadata
    )


@pytest.fixture
def sample_scam_analysis() -> ScamAnalysis:
    """Create a sample scam analysis."""
    return ScamAnalysis(
        is_scam=True,
        confidence=0.85,
        scam_type=ScamType.FAKE_OFFER,
        reasoning="Message contains lottery scam indicators",
        risk_indicators=["lottery", "winner", "urgent"]
    )


@pytest.fixture
def sample_session() -> Session:
    """Create a sample session."""
    return Session(
        session_id="session_001",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        status=SessionStatus.ACTIVE
    )


@pytest.fixture
def sample_persona_state() -> PersonaState:
    """Create a sample persona state."""
    return PersonaState(
        persona_type="curious_victim",
        personality_traits=["curious", "trusting", "elderly"],
        background_story="Retired teacher interested in online opportunities",
        current_mood="interested",
        knowledge_level="basic",
        trust_level=0.7
    )


# Hypothesis strategies for property-based testing
@st.composite
def message_strategy(draw):
    """Generate random Message instances."""
    return Message(
        sender=draw(st.sampled_from(["user", "agent", "scammer"])),
        text=draw(st.text(min_size=1, max_size=1000)),
        timestamp=draw(st.datetimes()),
        message_id=draw(st.text(min_size=1, max_size=50))
    )


@st.composite
def request_metadata_strategy(draw):
    """Generate random RequestMetadata instances."""
    return RequestMetadata(
        channel=draw(st.sampled_from(["SMS", "WhatsApp", "Email", "Telegram"])),
        language=draw(st.sampled_from(["en", "hi", "es", "fr"])),
        locale=draw(st.sampled_from(["en-US", "hi-IN", "es-ES", "fr-FR"])),
        source_ip=draw(st.one_of(st.none(), st.ip_addresses(v=4).map(str)))
    )


@st.composite
def message_request_strategy(draw):
    """Generate random MessageRequest instances."""
    return MessageRequest(
        session_id=draw(st.text(min_size=1, max_size=100)),
        message=draw(message_strategy()),
        conversation_history=draw(st.lists(message_strategy(), max_size=10)),
        metadata=draw(request_metadata_strategy())
    )


@st.composite
def scam_analysis_strategy(draw):
    """Generate random ScamAnalysis instances."""
    return ScamAnalysis(
        is_scam=draw(st.booleans()),
        confidence=draw(st.floats(min_value=0.0, max_value=1.0)),
        scam_type=draw(st.sampled_from(list(ScamType))),
        reasoning=draw(st.text(min_size=1, max_size=500)),
        risk_indicators=draw(st.lists(st.text(min_size=1, max_size=50), max_size=10))
    )