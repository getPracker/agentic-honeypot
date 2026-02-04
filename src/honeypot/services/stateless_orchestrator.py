"""Stateless Message Orchestrator service for serverless deployment."""

import logging
from typing import Optional
from datetime import datetime, timezone

from ..models.core import Message, MessageRequest, MessageResponse, EngagementMetrics
from ..models.session import Session, SessionStatus

from .stateless_session_manager import StatelessSessionManager
from .scam_detector import ScamDetector
from .ai_agent import AIAgent
from .intelligence_extractor import IntelligenceExtractor
from .callback_handler import CallbackHandler

logger = logging.getLogger(__name__)


class StatelessMessageProcessor:
    """
    Stateless orchestrator that processes messages without persistent state.
    Reconstructs session context from conversation history on each request.
    """

    def __init__(self):
        """Initialize all services."""
        self.session_manager = StatelessSessionManager()
        self.scam_detector = ScamDetector()
        self.ai_agent = AIAgent()
        self.intelligence_extractor = IntelligenceExtractor()
        self.callback_handler = CallbackHandler()

    async def process_message(self, request: MessageRequest) -> MessageResponse:
        """
        Process an incoming message request in a stateless manner.

        Flow:
        1. Reconstruct Session from conversation history
        2. Analyze current message for scam patterns
        3. Generate AI response if appropriate
        4. Extract intelligence from message
        5. Calculate engagement metrics
        6. Trigger callback if needed
        
        Args:
            request: The incoming message request.
            
        Returns:
            The structured response.
        """
        session_id = request.session_id
        incoming_msg = request.message
        
        try:
            # 1. Reconstruct Session from History
            session = self.session_manager.create_session_from_history(
                session_id=session_id,
                conversation_history=request.conversation_history,
                current_message=incoming_msg
            )
            
            # 2. Scam Detection on current message
            analysis = self.scam_detector.analyze(incoming_msg.text)
            self.session_manager.add_analysis_to_session(session, analysis)
            
            # 3. Intelligence Extraction from current message
            intelligence = self.intelligence_extractor.extract(incoming_msg.text)
            self._merge_intelligence(session, intelligence)
            
            # 4. Determine if we should engage
            should_engage = self._should_engage(session, analysis)
            agent_response_text = None
            
            if should_engage:
                # Generate AI response
                agent_response_text = self.ai_agent.generate_response(session, incoming_msg.text)
                
                if agent_response_text:
                    # Create agent message for context (not persisted, just for this request)
                    agent_msg = Message(
                        sender="agent",
                        text=agent_response_text,
                        timestamp=datetime.now(timezone.utc),
                        message_id=f"agent_{int(datetime.now(timezone.utc).timestamp())}"
                    )
                    session.add_message(agent_msg)
            
            # 5. Calculate Metrics
            metrics = EngagementMetrics(
                conversation_duration=session.get_conversation_duration(),
                message_count=session.get_message_count(),
                engagement_quality=self._calculate_engagement_quality(session, agent_response_text),
                intelligence_score=self._calculate_intelligence_score(session)
            )
            
            # 6. Prepare Response
            response = MessageResponse(
                status="success",
                scam_detected=analysis.is_scam,
                agent_response=agent_response_text,
                engagement_metrics=metrics,
                extracted_intelligence=self._serialize_intelligence(session),
                agent_notes=analysis.reasoning,
                session_id=session_id
            )
            
            # 7. Trigger Callback - Send Final Result to GUVI
            # Only send when scam is detected AND we have an agent response (engagement complete)
            if response.scam_detected and agent_response_text:
                try:
                    success = self.callback_handler.send_callback(session, response)
                    if success:
                        logger.info(f"✅ GUVI callback sent successfully for session {session_id}")
                    else:
                        logger.warning(f"⚠️ GUVI callback failed for session {session_id}")
                except Exception as e:
                    logger.error(f"❌ GUVI callback error for session {session_id}: {e}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message for session {session_id}: {e}", exc_info=True)
            
            # Return error response
            return MessageResponse(
                status="error",
                scam_detected=False,
                agent_response=None,
                engagement_metrics=EngagementMetrics(
                    conversation_duration=0,
                    message_count=1,
                    engagement_quality=0.0,
                    intelligence_score=0.0
                ),
                extracted_intelligence={},
                agent_notes=f"Processing error: {str(e)}",
                session_id=session_id
            )

    def _should_engage(self, session: Session, current_analysis) -> bool:
        """
        Determine if the AI agent should engage based on session context.
        
        Args:
            session: The reconstructed session
            current_analysis: Analysis of the current message
            
        Returns:
            True if agent should respond
        """
        print(f"🤔 [ORCHESTRATOR] Deciding whether to engage...")
        print(f"   📊 Current analysis - is_scam: {current_analysis.is_scam}")
        print(f"   📊 Current analysis - confidence: {current_analysis.confidence}")
        print(f"   📊 Current analysis - type: {current_analysis.scam_type.value}")
        
        # Engage if current message is detected as scam
        if current_analysis.is_scam:
            print(f"   ✅ Will engage: Current message is detected as scam")
            return True
        
        # Engage if any previous message in the session was a scam
        # (continuing an ongoing scam conversation)
        previous_scams = [analysis.is_scam for analysis in session.scam_analyses]
        print(f"   📚 Previous scam analyses: {previous_scams}")
        
        if any(analysis.is_scam for analysis in session.scam_analyses):
            print(f"   ✅ Will engage: Previous message(s) were scams (continuing conversation)")
            return True
        
        # Don't engage for non-scam messages
        print(f"   ❌ Will NOT engage: No scam detected in current or previous messages")
        return False

    def _merge_intelligence(self, session: Session, new_intel):
        """Merge new intelligence into session."""
        if not session.extracted_intelligence:
            session.extracted_intelligence = new_intel
            return

        current = session.extracted_intelligence
        
        # Merge unique items
        if new_intel.bank_accounts:
            existing_accounts = {b.account_number for b in current.bank_accounts}
            for acc in new_intel.bank_accounts:
                if acc.account_number not in existing_accounts:
                    current.bank_accounts.append(acc)
        
        if new_intel.upi_ids:
            current.upi_ids = list(set(current.upi_ids + new_intel.upi_ids))
        
        if new_intel.phone_numbers:
            existing_phones = {p.number for p in current.phone_numbers}
            for p in new_intel.phone_numbers:
                if p.number not in existing_phones:
                    current.phone_numbers.append(p)
        
        if new_intel.urls:
            existing_urls = {u.url for u in current.urls}
            for u in new_intel.urls:
                if u.url not in existing_urls:
                    current.urls.append(u)
        
        if new_intel.keywords:
            current.keywords = list(set(current.keywords + new_intel.keywords))

    def _calculate_engagement_quality(self, session: Session, agent_response: Optional[str]) -> float:
        """Calculate engagement quality score."""
        score = 0.0
        
        # Base score for having a response
        if agent_response:
            score += 0.3
        
        # Score based on conversation length
        msg_count = len(session.messages)
        if msg_count > 1:
            score += min(0.4, msg_count * 0.1)
        
        # Score based on intelligence extracted
        if session.extracted_intelligence:
            intel = session.extracted_intelligence
            intel_items = (
                len(intel.bank_accounts) + 
                len(intel.upi_ids) + 
                len(intel.phone_numbers) + 
                len(intel.urls)
            )
            score += min(0.3, intel_items * 0.1)
        
        return min(1.0, score)

    def _calculate_intelligence_score(self, session: Session) -> float:
        """Calculate intelligence extraction score."""
        if not session.extracted_intelligence:
            return 0.0
        
        intel = session.extracted_intelligence
        score = 0.0
        
        # Weight different types of intelligence
        score += len(intel.bank_accounts) * 0.3
        score += len(intel.upi_ids) * 0.2
        score += len(intel.phone_numbers) * 0.2
        score += len(intel.urls) * 0.1
        score += min(len(intel.keywords) * 0.02, 0.2)  # Cap keywords contribution
        
        return min(1.0, score)

    def _serialize_intelligence(self, session: Session) -> dict:
        """Serialize intelligence for API response."""
        if not session.extracted_intelligence:
            return {}
        
        try:
            from dataclasses import asdict
            return asdict(session.extracted_intelligence)
        except Exception as e:
            logger.warning(f"Failed to serialize intelligence: {e}")
            return {}