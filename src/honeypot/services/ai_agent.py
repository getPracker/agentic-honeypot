"""AI Agent service for generating conversational responses."""

import logging
import random
from typing import List, Optional

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI not available")

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠️ Google Generative AI not available")

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
        if self._settings.openai_api_key and OPENAI_AVAILABLE:
            try:
                self.openai_client = openai.Client(api_key=self._settings.openai_api_key)
                logger.info("✅ OpenAI client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        else:
            if not OPENAI_AVAILABLE:
                logger.warning("OpenAI package not available")
            if not self._settings.openai_api_key:
                logger.info("No OpenAI API key configured")
            
        if self._settings.gemini_api_key and GOOGLE_AVAILABLE:
            try:
                genai.configure(api_key=self._settings.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                logger.info("✅ Gemini client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")
                self.gemini_model = None
        else:
            if not GOOGLE_AVAILABLE:
                logger.warning("Google Generative AI package not available")
            if not self._settings.gemini_api_key:
                logger.info("No Gemini API key configured")
        
        if not self.openai_client and not self.gemini_model:
            logger.warning("No LLM API keys configured or packages available. Agent will run in mock mode.")

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
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI package not available")
            return None
            
        if not self.openai_client:
            logger.warning("OpenAI client not initialized")
            return None
            
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
        if not GOOGLE_AVAILABLE:
            logger.warning("Google Generative AI package not available")
            return None
            
        if not self.gemini_model:
            logger.warning("Gemini model not initialized")
            return None
            
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
        # Analyze the conversation to determine the best persona approach
        conversation_context = self._analyze_conversation_context(session)
        
        base_prompt = (
            "You are playing the role of a vulnerable person who might be targeted by scammers. "
            "Your goal is to keep the conversation going naturally while gathering information about potential scams. "
            
            "CRITICAL RULES:\n"
            "- NEVER reveal that you suspect this is a scam\n"
            "- NEVER say 'this seems suspicious' or similar phrases\n"
            "- Act naturally curious and somewhat naive\n"
            "- Ask follow-up questions to get more details\n"
            "- Show appropriate concern when they mention problems\n"
            "- Be helpful and cooperative\n"
            "- Use simple, everyday language\n"
            
            "PERSONA: You are a 65-year-old person who:\n"
            "- Is not very tech-savvy but tries to learn\n"
            "- Trusts people who sound official or helpful\n"
            "- Gets worried about financial or account problems\n"
            "- Asks for clarification when confused\n"
            "- Wants to resolve issues quickly\n"
            "- Sometimes shares personal details when asked\n"
            
            "RESPONSE STYLE:\n"
            "- Keep responses conversational and natural\n"
            "- Show genuine interest in what they're saying\n"
            "- Ask relevant follow-up questions\n"
            "- Express appropriate emotions (worry, excitement, confusion)\n"
            "- Avoid being overly suspicious or cautious\n"
            "- Stay engaged and responsive\n"
        )
        
        # Add context-specific guidance
        if conversation_context["likely_scam_type"]:
            scam_type = conversation_context["likely_scam_type"]
            if scam_type == "bank_fraud":
                base_prompt += (
                    "\nCONTEXT: This appears to be about banking/account issues. "
                    "Show concern about your account and ask what you need to do to fix it. "
                    "Be willing to provide information they request to 'verify' your account."
                )
            elif scam_type == "tech_support":
                base_prompt += (
                    "\nCONTEXT: This appears to be about computer/tech problems. "
                    "Act worried about your computer and grateful for their help. "
                    "Ask them to guide you through fixing the problem."
                )
            elif scam_type == "investment":
                base_prompt += (
                    "\nCONTEXT: This appears to be about investment opportunities. "
                    "Show interest in making money and ask for more details about the opportunity. "
                    "Express some excitement but also ask practical questions."
                )
        
        return base_prompt
    
    def _analyze_conversation_context(self, session: Session) -> dict:
        """Analyze the conversation to understand the context and likely scam type."""
        context = {
            "likely_scam_type": None,
            "urgency_level": "low",
            "information_requests": [],
            "conversation_stage": "initial"
        }
        
        if not session.messages:
            return context
        
        # Analyze all messages for patterns
        all_text = " ".join([msg.text.lower() for msg in session.messages])
        
        # Determine likely scam type
        if any(word in all_text for word in ["bank", "account", "blocked", "suspended", "verify"]):
            context["likely_scam_type"] = "bank_fraud"
        elif any(word in all_text for word in ["computer", "virus", "microsoft", "support", "infected"]):
            context["likely_scam_type"] = "tech_support"
        elif any(word in all_text for word in ["invest", "profit", "earn", "opportunity", "scheme"]):
            context["likely_scam_type"] = "investment"
        elif any(word in all_text for word in ["won", "lottery", "prize", "winner"]):
            context["likely_scam_type"] = "lottery"
        
        # Determine urgency level
        if any(word in all_text for word in ["urgent", "immediate", "now", "today", "expire"]):
            context["urgency_level"] = "high"
        elif any(word in all_text for word in ["soon", "quickly", "asap"]):
            context["urgency_level"] = "medium"
        
        # Determine conversation stage
        if len(session.messages) <= 2:
            context["conversation_stage"] = "initial"
        elif len(session.messages) <= 5:
            context["conversation_stage"] = "building_trust"
        else:
            context["conversation_stage"] = "information_gathering"
        
        return context

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
        """Generate a contextual mock/heuristic response for testing."""
        text_lower = text.lower()
        
        # Bank/Account related
        if any(word in text_lower for word in ["bank", "account", "blocked", "suspended", "verify"]):
            responses = [
                "Oh no! What happened to my account? I just used it yesterday. What do I need to do?",
                "This is very concerning. Can you tell me exactly what's wrong with my account?",
                "I'm worried about this. How can I check if my account is really blocked?",
                "Please help me understand what verification you need. I don't want to lose my money.",
                "Is this really from my bank? What information do you need to fix this?"
            ]
            return random.choice(responses)
        
        # UPI/Payment related
        if any(word in text_lower for word in ["upi", "paytm", "gpay", "payment", "transfer"]):
            responses = [
                "I'm not very good with these payment apps. Can you guide me step by step?",
                "My son set up UPI for me but I'm confused. What exactly do you need?",
                "I want to make sure I do this correctly. Can you explain it again?",
                "Is this safe? I've heard about people losing money online.",
                "What UPI ID? I'm not sure what that means. Can you help me find it?"
            ]
            return random.choice(responses)
        
        # Password/PIN/OTP related
        if any(word in text_lower for word in ["password", "pin", "otp", "code", "cvv"]):
            responses = [
                "Is that the number on the back of my card? The print is so small, I can barely read it.",
                "I have so many passwords, I get confused. Which one do you need?",
                "I just got a message with some numbers. Is that what you're asking for?",
                "My grandson usually helps me with these codes. Should I call him?",
                "I'm worried about sharing this. How do I know you're really from the bank?"
            ]
            return random.choice(responses)
        
        # Investment/Money related
        if any(word in text_lower for word in ["invest", "profit", "earn", "money", "scheme", "opportunity"]):
            responses = [
                "That sounds wonderful! I've been looking for ways to grow my savings. Tell me more.",
                "How much money do I need to start? I have some savings but not much.",
                "This sounds too good to be true. Can you explain how it works exactly?",
                "My late husband always said to be careful with investments. Is this really safe?",
                "I'm very interested! What do I need to do first?"
            ]
            return random.choice(responses)
        
        # Lottery/Prize related
        if any(word in text_lower for word in ["won", "winner", "lottery", "prize", "congratulations"]):
            responses = [
                "Really? I can't believe I won something! I never win anything. What did I win?",
                "This is so exciting! How much is the prize? What do I need to do to claim it?",
                "I don't remember entering any lottery. Are you sure this is for me?",
                "My neighbor got a similar message last month. Is this the same lottery?",
                "I'm so happy! Please tell me exactly what I need to do to get my prize."
            ]
            return random.choice(responses)
        
        # Tech Support related
        if any(word in text_lower for word in ["computer", "virus", "infected", "microsoft", "support", "error"]):
            responses = [
                "Oh dear! I knew something was wrong with my computer. It's been running slowly.",
                "I'm not good with computers. Can you help me fix this problem?",
                "My computer has been acting strange lately. What kind of virus is it?",
                "Should I be worried? I have important photos on my computer.",
                "Thank goodness you called! I was wondering who to contact about this."
            ]
            return random.choice(responses)
        
        # Questions that need specific responses
        if any(word in text_lower for word in ["what", "how", "when", "where", "why"]):
            if "name" in text_lower:
                return "My name is Margaret. Margaret Thompson. What do you need my name for?"
            elif "address" in text_lower:
                return "I live at 123 Oak Street. Do you need my full address for this?"
            elif "phone" in text_lower or "number" in text_lower:
                return "My phone number? It's the one you called me on. Do you need it written down?"
            elif "age" in text_lower:
                return "I'm 72 years old. Why do you need to know my age?"
            else:
                return "I'm not sure I understand the question. Can you explain it differently?"
        
        # Urgent/Time pressure
        if any(word in text_lower for word in ["urgent", "immediate", "now", "today", "hurry", "quick"]):
            responses = [
                "Oh my! I don't want to miss this. I'm ready to do whatever you need right now.",
                "This sounds very urgent. I'm available now. What should I do first?",
                "I'm worried about waiting too long. Please tell me exactly what to do.",
                "I don't want any problems. I'm ready to act immediately. Guide me through it.",
                "Time is important, I understand. I'm listening carefully to your instructions."
            ]
            return random.choice(responses)
        
        # Generic engagement responses for unclear messages
        generic_responses = [
            "I'm sorry, I didn't quite understand that. Can you explain it more clearly?",
            "Could you repeat that? I want to make sure I understand correctly.",
            "I'm a bit confused. Can you tell me more about what you need?",
            "This is important to me. Can you break it down step by step?",
            "I want to help, but I need you to explain this better. What exactly do you mean?",
            "I'm listening, but I'm not sure what you're asking. Can you be more specific?",
            "Let me make sure I understand. Are you saying that...?",
            "I'm trying to follow along. Can you give me more details?"
        ]
        
        return random.choice(generic_responses)

    def _is_unsafe_content(self, text: str) -> bool:
        """Check for unsafe content patterns."""
        unsafe_keywords = ["bomb", "suicide", "terror", "child abuse"] # Basic placeholder list
        return any(k in text.lower() for k in unsafe_keywords)

    def _is_unsafe_response(self, text: str) -> bool:
        """Check if generated response is unsafe."""
        # Prevent agent from generating hate speech or illegal advice
        # This is a fallback to model's own safety alignment
        return self._is_unsafe_content(text)
