"""Tests for ScamDetector service."""

import sys
import os
import unittest

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeypot.services.scam_detector import ScamDetector
from honeypot.models.scam import ScamType

class TestScamDetector(unittest.TestCase):
    def setUp(self):
        self.detector = ScamDetector()

    def test_clean_message(self):
        msg = "Hello, how are you today?"
        analysis = self.detector.analyze(msg)
        self.assertFalse(analysis.is_scam)
        self.assertEqual(analysis.scam_type, ScamType.UNKNOWN)

    def test_lottery_scam(self):
        msg = "Congratulations! You won a lottery of $1,000,000. Claim your prize now!"
        analysis = self.detector.analyze(msg)
        self.assertTrue(analysis.is_scam)
        self.assertEqual(analysis.scam_type, ScamType.FAKE_OFFER)
        self.assertGreaterEqual(analysis.confidence, 0.4)

    def test_bank_fraud(self):
        msg = "Your bank account has been blocked. Please provide your password and OTP to unblock."
        analysis = self.detector.analyze(msg)
        self.assertTrue(analysis.is_scam)
        self.assertEqual(analysis.scam_type, ScamType.BANK_FRAUD)
        self.assertIn("Action Request", analysis.risk_indicators) 
        # "blocked" is in rules, "provide" (not explicitly), "password" is in rules.

    def test_upi_fraud(self):
        msg = "I sent you money by mistake on GPay. Scan this QR code to refund immediately."
        analysis = self.detector.analyze(msg)
        self.assertTrue(analysis.is_scam)
        self.assertEqual(analysis.scam_type, ScamType.UPI_FRAUD)
        self.assertIn("Urgency", analysis.risk_indicators) # "immediately"

    def test_phishing_link(self):
        msg = "Urgent: Update your profile at http://suspicious-link.com to avoid suspension."
        analysis = self.detector.analyze(msg)
        self.assertTrue(analysis.is_scam)
        # Could be PHISHING or BANK_FRAUD depending on weights.
        # "Urgent" (0.2 Phishing), "http" (0.3 Phishing), "update" (0.2 Phishing), "suspension" (0.2 Bank)
        # Phishing sum = 0.7, Bank sum = 0.2. So Phishing wins.
        self.assertEqual(analysis.scam_type, ScamType.PHISHING)

    def test_investment_scam(self):
        msg = "Invest in Bitcoin now and get double returns guaranteed in 24 hours."
        analysis = self.detector.analyze(msg)
        self.assertTrue(analysis.is_scam)
        self.assertEqual(analysis.scam_type, ScamType.INVESTMENT_SCAM)
        
    def test_unknown_type_with_risks(self):
        # A message that doesn't trigger specific tough rules but has generic risks
        # This is harder to craft with current simple rules, but let's try.
        msg = "Kindly do the needful immediately."
        analysis = self.detector.analyze(msg)
        # "Kindly" (Salutation), "immediately" (Urgency).
        # Rules matches: None strong.
        # Max score 0.0 initially. +0.1 for risks = 0.1. < 0.4.
        # Should be NOT scam.
        self.assertFalse(analysis.is_scam)
        
        # Let's try one that borders.
        msg = "Kindly verify your login immediately."
        # "Kindly" (Risk), "verify" (Risk + Bank 0.3), "login" (Phishing 0.2), "immediately" (Risk + Phishing 0.2)
        # Bank score: 0.3.
        # Phishing score: 0.2 + 0.2 = 0.4.
        # Phishing wins with 0.4. >= 0.4 threshold.
        # Should be scam.
        analysis = self.detector.analyze(msg)
        self.assertTrue(analysis.is_scam)

if __name__ == '__main__':
    unittest.main()
