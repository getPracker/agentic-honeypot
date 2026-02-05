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
                (r"\b(click here|visit link|open this)\b", 0.3),
                (r"http[s]?://[^\s]{15,}", 0.3), # Malicious links are often long/obfuscated
                (r"\b(login|sign in|update.*payment|verify.*identity|account.*suspended)\b", 0.4),
                (r"\b(urgent|immediate.*|24 hours|expire.*now)\b", 0.2),
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
            ],
            ScamType.TECH_SUPPORT: [
                (r"\b(microsoft|apple|support|technician|virus|infected|malware|pc|computer)\b", 0.3),
                (r"\b(error.*code|scanning|alert|warning)\b", 0.3),
                (r"\b(toll.*free|call.*now|\+?1-?8[0-9]{2})\b", 0.4),
            ],
            ScamType.ROMANCE_SCAM: [
                (r"\b(love|honey|babe|darling|dear)\b", 0.2),
                (r"\b(lonely|widow|soldier|abroad|stuck)\b", 0.3),
                (r"\b(need.*help|money.*flight|hospital.*bill)\b", 0.4),
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
        print(f"🔍 [SCAM_DETECTOR] Starting analysis of message: '{message_text}'")
        message_lower = message_text.lower()
        print(f"📝 [SCAM_DETECTOR] Lowercase message: '{message_lower}'")
        
        best_scam_type = ScamType.UNKNOWN
        max_score = 0.0
        details = []
        detected_risks = []

        print("🚨 [SCAM_DETECTOR] Step 1: Checking risk indicators...")
        # 1. Identify Risk Indicators
        for pattern, label in self._risk_patterns:
            if re.search(pattern, message_lower):
                if label not in detected_risks:
                    detected_risks.append(label)
                    print(f"   ✅ Found risk indicator: '{label}' (pattern: {pattern})")
        
        print(f"📊 [SCAM_DETECTOR] Risk indicators found: {detected_risks}")

        print("🎯 [SCAM_DETECTOR] Step 2: Evaluating specific scam types...")
        # 2. Evaluate Specific Scam Types
        for scam_type, rules in self._rules.items():
            current_type_score = 0.0
            type_matches = []
            
            print(f"   🔍 Checking {scam_type.value}...")
            for pattern, weight in rules:
                if re.search(pattern, message_lower):
                    current_type_score += weight
                    type_matches.append(pattern)
                    print(f"      ✅ Match: '{pattern}' (weight: {weight}, running score: {current_type_score})")
            
            # Normalize score to max 1.0 per type naturally, but let's cap it
            current_type_score = min(1.0, current_type_score)
            
            if current_type_score > 0:
                print(f"   📊 {scam_type.value} final score: {current_type_score}")
            
            if current_type_score > max_score:
                max_score = current_type_score
                best_scam_type = scam_type
                print(f"   🏆 New best match: {scam_type.value} (score: {max_score})")
                
        print(f"🎯 [SCAM_DETECTOR] Step 3: Final verdict calculation...")
        print(f"   📊 Max score: {max_score}")
        print(f"   🏆 Best scam type: {best_scam_type.value}")
        
        # 3. Determine Final Verdict
        # Threshold for considering it a scam
        is_scam = max_score >= 0.5 
        print(f"   ⚖️ Initial scam verdict (score >= 0.5): {is_scam}")
        
        # If score is low but we have generic risk signs, maybe boost slightly?
        if not is_scam and detected_risks:
            print(f"   🔄 Boosting score due to risk indicators...")
            max_score += 0.1
            print(f"   📈 Boosted score: {max_score}")
            if max_score >= 0.4:
                is_scam = True
                if best_scam_type == ScamType.UNKNOWN:
                    best_scam_type = ScamType.PHISHING # Default fallback for generic risks often
                print(f"   ✅ Verdict changed to SCAM due to risk boost")
        
        # Prepare reasoning
        reasoning = "No significant scam patterns detected."
        if is_scam:
            patterns_str = ", ".join(detected_risks) if detected_risks else "specific keywords"
            reasoning = f"Detected potential {best_scam_type.value} with confidence {max_score:.2f}. " \
                        f"Indicators: {patterns_str}"
        
        print(f"🏁 [SCAM_DETECTOR] Final Analysis:")
        print(f"   🚨 Is Scam: {is_scam}")
        print(f"   📊 Confidence: {max_score:.2f}")
        print(f"   🏷️ Type: {best_scam_type.value}")
        print(f"   📝 Reasoning: {reasoning}")
        
        result = ScamAnalysis(
            is_scam=is_scam,
            confidence=round(max_score, 2),
            scam_type=best_scam_type if is_scam else ScamType.UNKNOWN,
            reasoning=reasoning,
            risk_indicators=detected_risks
        )
        
        print(f"✅ [SCAM_DETECTOR] Analysis complete: {result}")
        return result
