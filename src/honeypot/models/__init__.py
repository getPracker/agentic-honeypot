"""Data models for the honeypot system."""

from .core import (
    Message,
    MessageRequest,
    MessageResponse,
    RequestMetadata,
    EngagementMetrics,
)
from .scam import (
    ScamAnalysis,
    ScamType,
    ScamIntelligence,
    BankAccount,
    PhoneNumber,
    URL,
    BehaviorPatterns,
)
from .session import (
    Session,
    SessionStatus,
    ConversationContext,
    PersonaState,
    EngagementStrategy,
    ConversationStage,
)

__all__ = [
    # Core models
    "Message",
    "MessageRequest", 
    "MessageResponse",
    "RequestMetadata",
    "EngagementMetrics",
    # Scam models
    "ScamAnalysis",
    "ScamType",
    "ScamIntelligence",
    "BankAccount",
    "PhoneNumber",
    "URL",
    "BehaviorPatterns",
    # Session models
    "Session",
    "SessionStatus",
    "ConversationContext",
    "PersonaState",
    "EngagementStrategy",
    "ConversationStage",
]