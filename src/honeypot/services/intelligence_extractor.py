"""Intelligence extraction service."""

import re
import logging
from typing import List, Optional
from urllib.parse import urlparse

from ..models.scam import (
    ScamIntelligence, BankAccount, PhoneNumber, URL, BehaviorPatterns
)

logger = logging.getLogger(__name__)


class IntelligenceExtractor:
    """
    Extracts structured intelligence from message content.
    Identifies entities like bank accounts, phone numbers, UPI IDs, and URLs.
    """

    def __init__(self):
        """Initialize extraction patterns."""
        # Regex Patterns
        self._patterns = {
            "upi": r"[\w\.\-]+@[\w\.\-]+",  # Basic UPI pattern (e.g., name@bank)
            "phone": r"(\+?91[\-\s]?)?[6789]\d{9}",  # Indian mobile numbers
            "bank_account": r"\b\d{9,18}\b",  # Generic 9-18 digit numbers often used for accounts
            "ifsc": r"[A-Z]{4}0[A-Z0-9]{6}",  # Indian Financial System Code
            "url": r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        }
        
        self._behavior_keywords = {
            "urgency": ["urgent", "immediately", "hurry", "asap", "24 hours"],
            "financial": ["invest", "profit", "return", "bank", "account", "money"],
            "coercion": ["police", "arrest", "cbi", "customs", "blocked"]
        }

    def extract(self, message_text: str) -> ScamIntelligence:
        """
        Extract intelligence from a message.
        
        Args:
            message_text: The message content.
            
        Returns:
            ScamIntelligence object with extracted data.
        """
        text_lower = message_text.lower()
        
        # 1. Extract Entities
        bank_accounts = self._extract_bank_accounts(message_text)
        upi_ids = self._extract_upi_ids(message_text)
        phone_numbers = self._extract_phone_numbers(message_text)
        urls = self._extract_urls(message_text)
        
        # 2. Extract Keywords/Behavior
        keywords = self._extract_keywords(text_lower)
        behavior_patterns = self._analyze_behavior(text_lower)
        
        return ScamIntelligence(
            bank_accounts=bank_accounts,
            upi_ids=upi_ids,
            phone_numbers=phone_numbers,
            urls=urls,
            keywords=keywords,
            behavior_patterns=behavior_patterns
        )

    def _extract_bank_accounts(self, text: str) -> List[BankAccount]:
        """Extract potential bank account numbers."""
        accounts = []
        # Find pure digit sequences that look like account numbers
        matches = re.finditer(self._patterns["bank_account"], text)
        
        # Also look for IFSC nearby
        ifsc_matches = set(re.findall(self._patterns["ifsc"], text))
        primary_ifsc = list(ifsc_matches)[0] if ifsc_matches else None
        
        for match in matches:
            acc_num = match.group()
            # Simple heuristic to avoid 10-digit phone numbers being confused as accounts
            # If it starts with 6-9 and is 10 digits, likely phone.
            if len(acc_num) == 10 and acc_num[0] in '6789':
                continue
                
            accounts.append(BankAccount(
                account_number=acc_num,
                ifsc_code=primary_ifsc,
                confidence=0.8 if primary_ifsc else 0.5
            ))
        return accounts

    def _extract_upi_ids(self, text: str) -> List[str]:
        """Extract UPI IDs."""
        # Simple regex, might need refinement to avoid emails
        matches = re.findall(self._patterns["upi"], text)
        # Filter to ensure it looks like a UPI handle (simple validation)
        valid_upi = []
        for m in matches:
            m = m.rstrip('.') # Remove trailing dot if picked up from sentence end
            if "gmail" in m or "yahoo" in m:
                continue # Likely email
            valid_upi.append(m)
        return list(set(valid_upi))

    def _extract_phone_numbers(self, text: str) -> List[PhoneNumber]:
        """Extract phone numbers."""
        matches = re.finditer(self._patterns["phone"], text)
        phones = []
        seen = set()
        
        for match in matches:
            raw = match.group()
            clean = raw.replace(" ", "").replace("-", "")
            if clean in seen:
                continue
            seen.add(clean)
            
            phones.append(PhoneNumber(
                number=clean,
                country_code="+91", # Defaulting to India for this honeypot context
                confidence=0.9
            ))
        return phones

    def _extract_urls(self, text: str) -> List[URL]:
        """Extract and analyze URLs."""
        matches = re.findall(self._patterns["url"], text)
        urls = []
        for m in matches:
            parsed = urlparse(m)
            urls.append(URL(
                url=m,
                domain=parsed.netloc,
                is_malicious=False # Needs external lookup, default False
            ))
        return urls

    def _extract_keywords(self, text_lower: str) -> List[str]:
        """Extract significant keywords."""
        found = []
        for category, words in self._behavior_keywords.items():
            for word in words:
                if word in text_lower:
                    found.append(word)
        return list(set(found))

    def _analyze_behavior(self, text_lower: str) -> BehaviorPatterns:
        """Analyze text for behavioral patterns."""
        urgency = [w for w in self._behavior_keywords["urgency"] if w in text_lower]
        
        # Simple implementation - could be more complex NLP
        return BehaviorPatterns(
            urgency_indicators=urgency,
            social_engineering_tactics=[], 
            linguistic_patterns=[],
            timing_patterns=[]
        )
