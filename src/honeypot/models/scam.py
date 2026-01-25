"""Scam detection and intelligence models."""

from enum import Enum
from typing import List, Optional
from dataclasses import dataclass


class ScamType(Enum):
    """Types of scams that can be detected."""
    BANK_FRAUD = "bank_fraud"
    UPI_FRAUD = "upi_fraud"
    PHISHING = "phishing"
    FAKE_OFFER = "fake_offer"
    INVESTMENT_SCAM = "investment_scam"
    ROMANCE_SCAM = "romance_scam"
    TECH_SUPPORT = "tech_support"
    UNKNOWN = "unknown"


@dataclass
class ScamAnalysis:
    """Analysis results for scam detection."""
    is_scam: bool
    confidence: float  # 0.0 to 1.0
    scam_type: ScamType
    reasoning: str
    risk_indicators: List[str]


@dataclass
class BankAccount:
    """Extracted bank account information."""
    account_number: str
    ifsc_code: Optional[str] = None
    bank_name: Optional[str] = None
    confidence: float = 0.0


@dataclass
class PhoneNumber:
    """Extracted phone number information."""
    number: str
    country_code: str
    is_verified: bool = False
    confidence: float = 0.0


@dataclass
class URL:
    """Extracted URL information."""
    url: str
    domain: str
    is_malicious: bool = False
    threat_type: Optional[str] = None


@dataclass
class BehaviorPatterns:
    """Behavioral patterns identified in scammer interactions."""
    urgency_indicators: List[str]
    social_engineering_tactics: List[str]
    linguistic_patterns: List[str]
    timing_patterns: List[str]


@dataclass
class ScamIntelligence:
    """Structured intelligence extracted from scam conversations."""
    bank_accounts: List[BankAccount]
    upi_ids: List[str]
    phone_numbers: List[PhoneNumber]
    urls: List[URL]
    keywords: List[str]
    behavior_patterns: BehaviorPatterns
    
    def __post_init__(self):
        """Initialize empty lists if None."""
        if self.bank_accounts is None:
            self.bank_accounts = []
        if self.upi_ids is None:
            self.upi_ids = []
        if self.phone_numbers is None:
            self.phone_numbers = []
        if self.urls is None:
            self.urls = []
        if self.keywords is None:
            self.keywords = []
        if self.behavior_patterns is None:
            self.behavior_patterns = BehaviorPatterns([], [], [], [])