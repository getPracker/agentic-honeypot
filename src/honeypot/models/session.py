"""Session and conversation management models."""

from enum import Enum
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from .core import Message
from .scam import ScamAnalysis, ScamIntelligence


class SessionStatus(Enum):
    """Status of a conversation session."""
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    ERROR = "error"


class ConversationStage(Enum):
    """Stage of the conversation flow."""
    INITIAL_CONTACT = "initial_contact"
    ENGAGEMENT = "engagement"
    INFORMATION_GATHERING = "information_gathering"
    INTELLIGENCE_EXTRACTION = "intelligence_extraction"
    CONCLUSION = "conclusion"


class EngagementStrategy(Enum):
    """Strategy for engaging with the scammer."""
    CURIOUS_VICTIM = "curious_victim"
    EAGER_PARTICIPANT = "eager_participant"
    CAUTIOUS_INQUIRER = "cautious_inquirer"
    TECHNICAL_QUESTIONER = "technical_questioner"


@dataclass
class PersonaState:
    """State of the AI agent's persona."""
    persona_type: str
    personality_traits: List[str]
    background_story: str
    current_mood: str
    knowledge_level: str
    trust_level: float  # 0.0 to 1.0
    
    def __post_init__(self):
        """Initialize default values."""
        if self.personality_traits is None:
            self.personality_traits = []


@dataclass
class Session:
    """Represents a conversation session."""
    session_id: str
    created_at: datetime
    updated_at: datetime
    status: SessionStatus
    messages: List[Message] = field(default_factory=list)
    scam_analyses: List[ScamAnalysis] = field(default_factory=list)
    extracted_intelligence: Optional[ScamIntelligence] = None
    agent_notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: Message) -> None:
        """Add a message to the session."""
        self.messages.append(message)
        self.updated_at = datetime.now(timezone.utc)
    
    def add_analysis(self, analysis: ScamAnalysis) -> None:
        """Add a scam analysis to the session."""
        self.scam_analyses.append(analysis)
        self.updated_at = datetime.now(timezone.utc)
    
    def get_message_count(self) -> int:
        """Get the total number of messages in the session."""
        return len(self.messages)
    
    def get_conversation_duration(self) -> int:
        """Get conversation duration in seconds."""
        if not self.messages:
            return 0
        return int((self.updated_at - self.created_at).total_seconds())


@dataclass
class ConversationContext:
    """Context for managing conversation state."""
    session: Session
    current_persona: PersonaState
    engagement_strategy: EngagementStrategy
    conversation_stage: ConversationStage
    
    def update_stage(self, new_stage: ConversationStage) -> None:
        """Update the conversation stage."""
        self.conversation_stage = new_stage
    
    def update_persona_trust(self, trust_delta: float) -> None:
        """Update the persona's trust level."""
        new_trust = max(0.0, min(1.0, self.current_persona.trust_level + trust_delta))
        self.current_persona.trust_level = new_trust