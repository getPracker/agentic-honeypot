"""AI Agent service for generating conversational responses."""

import logging
import random
from typing import List, Optional

import openai
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config.settings import get_settings
from ..models.core import Message
from ..models.session import Session, PersonaState
from ..models.scam import ScamAnalysis, ScamType

logger = logging.getLogger(__name__)


class AIAgent:
    """
    AI Agent responsible for engaging with scammers.
    Manages persona, generates responses, and ensures safety.
    """

    def __init__(self):
        """Initialize the AI agent."""
        self._settings = get_settings()
        self.openai_client = None
        self.gemini_model = None
        self._setup_providers()
        
        # Hardcoded personas for now - could be moved to config or database
        self._personas = [
            {
                "type": "elderly_victim",
                "traits": ["trusting", "technologically illiterate", "polite", "confused"],
                "background": "72-year-old retired school teacher living alone.",
                "style": "Uses formal language, types slowly, asks for clarification often."
            },
            {
                "type": "naive_student",
                "traits": ["eager", "broke", "optimistic", "careless"],
                "background": "20-year-old college student looking for quick cash.",
                "style": "Uses slang, emojis, replies fast, very interested in money."
            },
            {
                "type": "curious_skeptic",
                "traits": ["cautious", "detail-oriented", "slow", "methodical"],
                "background": "45-year-old accountant who verifies everything.",
                "style": "Asks specific questions, references rules or policies."
            }
        ]

    def _setup_providers(self):
        """Setup LLM providers based on configuration."""
        if self._settings.openai_api_key:
            self.openai_client = openai.Client(api_key=self._settings.openai_api_key)
            
        if self._settings.gemini_api_key:
            genai.configure(api_key=self._settings.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        
        if not self.openai_client and not self.gemini_model:
            logger.warning("No LLM API keys configured. agent will run in detailed mock mode.")

    def select_persona(self, analysis: ScamAnalysis) -> PersonaState:
        """
        Select an appropriate persona based on the detected scam type.
        
        Args:
            analysis: The scam analysis results.
            
        Returns:
            A new PersonaState object.
        """
        # Logic to pick persona based on scam type
        # For Investment scams -> Naive Student
        # For Tech Support -> Elderly Victim
        # Default -> Random
        
        if analysis.scam_type == ScamType.TECH_SUPPORT:
            persona_def = self._personas[0] # Elderly
        elif analysis.scam_type == ScamType.INVESTMENT_SCAM:
            persona_def = self._personas[1] # Student
        else:
            persona_def = random.choice(self._personas)
            
        return PersonaState(
            persona_type=persona_def["type"],
            personality_traits=persona_def["traits"],
            background_story=persona_def["background"] + f" Style: {persona_def['style']}",
            current_mood="neutral",
            knowledge_level="low",
            trust_level=0.5
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_response(self, session: Session, current_message: str) -> Optional[str]:
        """
        Generate a response to the scammer.
        
        Args:
            session: The interaction session context.
            current_message: The latest message from the scammer.
            
        Returns:
            Generated response string or None if failed.
        """
        # Safety check: Do not engage if we strongly feel it's unsafe or if specific keywords are triggered
        if self._is_unsafe_content(current_message):
            logger.warning("Unsafe content detected in input, disengaging or careful.")
        
        prompt = self._construct_system_prompt(session)
        
        # Use Gemini if preferred or OpenAI not avail
        if self._settings.default_llm_provider == "gemini" and self.gemini_model:
            resp = self._generate_gemini_response(prompt, session, current_message)
            if resp: return resp
            
        if self.openai_client:
            resp = self._generate_openai_response(prompt, session, current_message)
            if resp: return resp

        return self._generate_mock_response(current_message)

    def _generate_openai_response(self, prompt: str, session: Session, current_message: str) -> Optional[str]:
        """Generate response using OpenAI."""
        messages = self._construct_message_history(session, current_message)
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt}] + messages,
                max_tokens=150,
                temperature=0.8
            )
            content = response.choices[0].message.content
            if self._is_unsafe_response(content):
                return "I'm sorry, I didn't quite catch that. Could you explain again?"
            return content
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            return None

    def _generate_gemini_response(self, prompt: str, session: Session, current_message: str) -> Optional[str]:
        """Generate response using Gemini."""
        try:
            # Gemini has different chat structure. 
            # We can use chat.start_chat(history=...)
            history = []
            # Convert messages to Gemini format (user/model)
            for msg in session.messages:
                role = "model" if msg.sender == "agent" else "user"
                history.append({"role": role, "parts": [msg.text]})
            
            chat = self.gemini_model.start_chat(history=history)
            
            # Combine system prompt with current message roughly, or send as 0-shot context
            # Gemini Pro is chat tuned. We can prepend prompt to first user message if history empty, 
            # or just rely on context if history is long.
            # Best practice: system instructions if API supports (Generic implementation here)
            
            full_input = f"{prompt}\n\nUser says: {current_message}"
            response = chat.send_message(full_input)
            
            content = response.text
            if self._is_unsafe_response(content):
                return "I'm sorry, I didn't quite catch that. Could you explain again?"
            return content
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            return None

    def _construct_system_prompt(self, session: Session) -> str:
        """Construct the system prompt for the persona."""
        # Check if we have a persona stored, otherwise default
        # Ideally, Session object would have this. We defined it in models/session.py but 
        # Session struct there didn't seem to have explicit 'persona' field, 
        # it was in ConversationContext class.
        # For this implementation, let's assume we can fetch it or use a default.
        
        # Default fallback
        persona_text = "You are an elderly person who is not very tech-savvy."
        
        return (
            f"{persona_text} "
            "You are chatting with someone who might be a scammer. "
            "Your goal is to waste their time and keep them talking without revealing you know it's a scam. "
            "Do NOT give away real personal sensitive info (use fake info). "
            "Act confused often. Ask for clarifications."
        )

    def _construct_message_history(self, session: Session, current_msg: str) -> List[dict]:
        """Convert session history to LLM format."""
        history = []
        for msg in session.messages:
            role = "assistant" if msg.sender == "agent" else "user"
            history.append({"role": role, "content": msg.text})
        
        # Append current if not already in session (depending on flow)
        # Usually orchestrator adds it. If it's already last, don't add.
        if not session.messages or session.messages[-1].text != current_msg:
             history.append({"role": "user", "content": current_msg})
             
        return history

    def _generate_mock_response(self, text: str) -> str:
        """Generate a mock/heuristic response for testing."""
        text_lower = text.lower()
        if "bank" in text_lower or "account" in text_lower:
            return "Oh dear, I seem to have lost my bank book. Which bank is this again?"
        if "password" in text_lower or "pin" in text_lower:
            return "Is that the number on the back of the card? The print is so small."
        if "invest" in text_lower:
            return "That sounds wonderful. My grandson usually handles my money, but tell me more."
        return "I'm sorry, I'm a bit hard of hearing. Can you type that again clearly?"

    def _is_unsafe_content(self, text: str) -> bool:
        """Check for unsafe content patterns."""
        unsafe_keywords = ["bomb", "suicide", "terror", "child abuse"] # Basic placeholder list
        return any(k in text.lower() for k in unsafe_keywords)

    def _is_unsafe_response(self, text: str) -> bool:
        """Check if generated response is unsafe."""
        # Prevent agent from generating hate speech or illegal advice
        # This is a fallback to model's own safety alignment
        return self._is_unsafe_content(text)
