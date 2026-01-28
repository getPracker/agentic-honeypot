"""Message Orchestrator service."""

import logging
from typing import Optional
from datetime import datetime, timezone

from ..models.core import Message, MessageRequest, MessageResponse, EngagementMetrics
from ..models.session import Session, SessionStatus
from ..models.scam import ScamAnalysis, ScamType

from .session_manager import SessionManager
from .scam_detector import ScamDetector
from .ai_agent import AIAgent
from .intelligence_extractor import IntelligenceExtractor
from .callback_handler import CallbackHandler

logger = logging.getLogger(__name__)


class MessageProcessor:
    """
    Orchestrates the processing of incoming messages.
    Coordinating Session, Detection, Agent, Intelligence, and Callback components.
    """

    def __init__(self):
        """Initialize all services."""
        self.session_manager = SessionManager()
        self.scam_detector = ScamDetector()
        self.ai_agent = AIAgent()
        self.intelligence_extractor = IntelligenceExtractor()
        self.callback_handler = CallbackHandler()

    async def process_message(self, request: MessageRequest) -> MessageResponse:
        """
        Process an incoming message request.

        Flow:
        1. Retrieve/Create Session
        2. Validate History
        3. Analyze for Scam
        4. Engage (AI Agent) if appropriate
        5. Extract Intelligence
        6. Determine Status & Metrics
        7. Trigger Callback (if session complete or scam definitive)
        
        Args:
            request: The incoming message request.
            
        Returns:
            The structured response.
        """
        session_id = request.session_id
        incoming_msg = request.message
        
        # 1. Session Management
        session = self.session_manager.get_session(session_id)
        if not session:
            try:
                session = self.session_manager.create_session(session_id)
            except ValueError as e:
                # Session might have been created concurrently or limit reached
                logger.error(f"Failed to create session {session_id}: {e}")
                # Try getting it again just in case
                session = self.session_manager.get_session(session_id)
                if not session:
                    raise Exception("System busy or session error")

        # Add message to session
        self.session_manager.add_message_to_session(session_id, incoming_msg)
        
        # 2. History Validation (Optional based on requirements urgency)
        if request.conversation_history:
             if not self.session_manager.validate_history(session_id, request.conversation_history):
                 logger.warning(f"History mismatch for session {session_id}")
                 # We could error out or just log. For honeypot robustness, we log and proceed usually.

        # 3. Scam Detection
        # We classify ONLY on the new message usually, but could use history context
        # For MVP rule-based, per-message is fine.
        analysis = self.scam_detector.analyze(incoming_msg.text)
        session.add_analysis(analysis) # Track analysis
        
        # 4. Intelligence Extraction
        # Extract from current message
        intelligence = self.intelligence_extractor.extract(incoming_msg.text)
        # Update session intelligence (merge logic)
        self._merge_intelligence(session, intelligence)
        
        # 5. Engagement (AI Agent)
        agent_response_text = None
        # Only engage if scam is suspected OR we are already in an active scam conversation
        # If UNKNOWN and no prior scam detection, we might choose NOT to reply or reply generically?
        # Requirement 54: "WHEN no scam is detected ... return negative classification without engaging"
        
        # Check if this session has EVER detected a scam
        is_scam_context = any(a.is_scam for a in session.scam_analyses)
        
        if analysis.is_scam or is_scam_context:
            # We are in a scam flow
            # Select Persona if not set (conceptually)
            # Generate response
            agent_response_text = self.ai_agent.generate_response(session, incoming_msg.text)
            
            if agent_response_text:
                # Add agent msg to session
                agent_msg = Message(
                    sender="agent",
                    text=agent_response_text,
                    timestamp=datetime.now(timezone.utc),
                    message_id=f"agent_{int(datetime.now(timezone.utc).timestamp())}"
                )
                self.session_manager.add_message_to_session(session_id, agent_msg)
        
        # 6. Prepare Response
        metrics = EngagementMetrics(
            conversation_duration=session.get_conversation_duration(),
            message_count=session.get_message_count(),
            engagement_quality=0.8 if agent_response_text else 0.0, # Placeholder logic
            intelligence_score=self._calculate_intelligence_score(session)
        )
        
        response = MessageResponse(
            status="success",
            scam_detected=analysis.is_scam,
            agent_response=agent_response_text,
            engagement_metrics=metrics,
            extracted_intelligence=self._serialize_intelligence(session),
            agent_notes=analysis.reasoning,
            session_id=session_id
        )
        
        # 7. Callback Trigger
        # Trigger on every turn? Or only conclusion?
        # Req 100: "WHEN a conversation concludes"
        # Since we don't have explicit "end" signal from scammer, we might callback heavily
        # Or callback on every significant update?
        # For this hackathon/MVP, let's callback on every scam turn to stream updates?
        # Or maybe only if we extracted something new?
        # Let's callback always for visibility if scam detected
        if response.scam_detected:
            self.callback_handler.send_callback(session, response)

        return response

    def _merge_intelligence(self, session: Session, new_intel):
        """Merge new intelligence into session storage."""
        if not session.extracted_intelligence:
            session.extracted_intelligence = new_intel
            return

        current = session.extracted_intelligence
        
        # Append unique lists
        # Banks
        existing_accs = {b.account_number for b in current.bank_accounts}
        for acc in new_intel.bank_accounts:
            if acc.account_number not in existing_accs:
                current.bank_accounts.append(acc)
        
        # UPI
        current.upi_ids = list(set(current.upi_ids + new_intel.upi_ids))
        
        # Phones
        existing_phones = {p.number for p in current.phone_numbers}
        for p in new_intel.phone_numbers:
            if p.number not in existing_phones:
                current.phone_numbers.append(p)
                
        # URLs
        existing_urls = {u.url for u in current.urls}
        for u in new_intel.urls:
            if u.url not in existing_urls:
                current.urls.append(u)
                
        # Keywords
        current.keywords = list(set(current.keywords + new_intel.keywords))

    def _calculate_intelligence_score(self, session: Session) -> float:
        """Calculate a simple score based on amount of extracted data."""
        if not session.extracted_intelligence:
            return 0.0
        intel = session.extracted_intelligence
        score = 0.0
        score += len(intel.bank_accounts) * 0.3
        score += len(intel.upi_ids) * 0.2
        score += len(intel.phone_numbers) * 0.2
        return min(1.0, score)

    def _serialize_intelligence(self, session: Session) -> dict:
        """Serialize intelligence for API response."""
        if not session.extracted_intelligence:
            return {}
        from dataclasses import asdict
        return asdict(session.extracted_intelligence)
