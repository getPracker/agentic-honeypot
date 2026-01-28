"""Scam detection service."""

import re
from typing import List, Tuple
import logging

from ..models.scam import ScamAnalysis, ScamType

logger = logging.getLogger(__name__)


class ScamDetector:
    """
    Rule-based scam detection engine.
    Analyzes message content to identify potential scams and classify them.
    """

    def __init__(self):
        """Initialize the scam detector with detection rules."""
        # Rules organization: Type -> List of (regex/keyword, weight)
        # Weights are summed up to calculate confidence.
        self._rules = {
            ScamType.BANK_FRAUD: [
                (r"\b(account.*number|ac no)\b", 0.3),
                (r"\b(password|pin|otp|cvv)\b", 0.4),
                (r"\b(verify.*account|kyc|adhaar|pan card|unblock)\b", 0.3),
                (r"\b(blocked|suspended|deactivated)\b", 0.2),
            ],
            ScamType.UPI_FRAUD: [
                (r"\b(paytm|gpay|phonepe|upi)\b", 0.2),
                (r"\b(receive.*money|cashback|refund)\b", 0.3),
                (r"\b(scan.*qr|qr.*code)\b", 0.4),
                (r"\b(enter.*pin)\b", 0.5),
            ],
            ScamType.PHISHING: [
                (r"\b(click|visit|link)\b", 0.2),
                (r"http[s]?://", 0.3),
                (r"\b(login|sign in|update)\b", 0.2),
                (r"\b(urgent|immediate.*|24 hours)\b", 0.2),
            ],
            ScamType.FAKE_OFFER: [
                (r"\b(winner|won|lottery|prize)\b", 0.5),
                (r"\b(congratulations|lucky)\b", 0.3),
                (r"\b(claim|redeem)\b", 0.3),
                (r"\b(free|gift)\b", 0.2),
            ],
            ScamType.INVESTMENT_SCAM: [
                (r"\b(invest|crypto|bitcoin|profit|return)\b", 0.4),
                (r"\b(guaranteed|double|earning)\b", 0.4),
                (r"\b(opportunity|scheme)\b", 0.2),
            ]
        }
        
        # Universal risk indicators (adds small confidence to any match)
        self._risk_patterns = [
            (r"\b(urgent|hurry|immediate.*)\b", "Urgency"),
            (r"\b(kindly|dear|beloved)\b", "Suspicious Salutation"),
            (r"\b(verify|update|provide|submit)\b", "Action Request"),
        ]

    def analyze(self, message_text: str) -> ScamAnalysis:
        """
        Analyze a message for scam content.
        
        Args:
            message_text: The content of the message to analyze.
            
        Returns:
            ScamAnalysis object with results.
        """
        message_lower = message_text.lower()
        
        best_scam_type = ScamType.UNKNOWN
        max_score = 0.0
        details = []
        detected_risks = []

        # 1. Identify Risk Indicators
        for pattern, label in self._risk_patterns:
            if re.search(pattern, message_lower):
                if label not in detected_risks:
                    detected_risks.append(label)

        # 2. Evaluate Specific Scam Types
        for scam_type, rules in self._rules.items():
            current_type_score = 0.0
            type_matches = []
            
            for pattern, weight in rules:
                if re.search(pattern, message_lower):
                    current_type_score += weight
                    type_matches.append(pattern)
            
            # Normalize score to max 1.0 per type naturally, but let's cap it
            current_type_score = min(1.0, current_type_score)
            
            if current_type_score > max_score:
                max_score = current_type_score
                best_scam_type = scam_type
                # details = type_matches 
                
        # 3. Determine Final Verdict
        # Threshold for considering it a scam
        is_scam = max_score >= 0.4 
        
        # If score is low but we have generic risk signs, maybe boost slightly?
        if not is_scam and detected_risks:
            max_score += 0.1
            if max_score >= 0.4:
                is_scam = True
                if best_scam_type == ScamType.UNKNOWN:
                    best_scam_type = ScamType.PHISHING # Default fallback for generic risks often
        
        # Prepare reasoning
        reasoning = "No significant scam patterns detected."
        if is_scam:
            patterns_str = ", ".join(detected_risks) if detected_risks else "specific keywords"
            reasoning = f"Detected potential {best_scam_type.value} with confidence {max_score:.2f}. " \
                        f"Indicators: {patterns_str}"
        
        return ScamAnalysis(
            is_scam=is_scam,
            confidence=round(max_score, 2),
            scam_type=best_scam_type if is_scam else ScamType.UNKNOWN,
            reasoning=reasoning,
            risk_indicators=detected_risks
        )
