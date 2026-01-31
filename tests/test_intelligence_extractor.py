"""Tests for IntelligenceExtractor service."""

import sys
import os
import unittest

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeypot.services.intelligence_extractor import IntelligenceExtractor

class TestIntelligenceExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = IntelligenceExtractor()

    def test_extract_bank_account(self):
        msg = "Please deposit to account 123456789012 IFSC HDFC0001234."
        intelligence = self.extractor.extract(msg)
        
        self.assertTrue(len(intelligence.bank_accounts) > 0)
        acc = intelligence.bank_accounts[0]
        self.assertEqual(acc.account_number, "123456789012")
        self.assertEqual(acc.ifsc_code, "HDFC0001234")
        self.assertEqual(acc.confidence, 0.8)

    def test_extract_upi(self):
        msg = "Pay me at merchant@okaxis or user@ybl. Do not email me at user@gmail.com."
        intelligence = self.extractor.extract(msg)
        
        # Should match merchant@okaxis and user@ybl, but NOT user@gmail.com (heuristic)
        upi_set = set(intelligence.upi_ids)
        self.assertIn("merchant@okaxis", upi_set)
        self.assertIn("user@ybl", upi_set)
        
        # Check that gmail is excluded by our simple filter
        # The regex matches gmail.com, but our filter logic excludes 'gmail'
        # Let's verify valid_upi logic
        self.assertFalse(any("gmail" in u for u in upi_set))

    def test_extract_phone_number(self):
        msg = "Call me on 9876543210 or +91-9876543211."
        intelligence = self.extractor.extract(msg)
        
        self.assertEqual(len(intelligence.phone_numbers), 2)
        extracted_nums = [p.number for p in intelligence.phone_numbers]
        
        # Check specific numbers are present
        self.assertIn("9876543210", extracted_nums)
        # The specific regex cleaning logic removes - and whitespace
        self.assertIn("+919876543211", extracted_nums)

    def test_extract_url(self):
        msg = "Visit http://fake-bank.com/login now."
        intelligence = self.extractor.extract(msg)
        
        self.assertEqual(len(intelligence.urls), 1)
        self.assertEqual(intelligence.urls[0].url, "http://fake-bank.com/login")
        self.assertEqual(intelligence.urls[0].domain, "fake-bank.com")

    def test_extract_behavior_keywords(self):
        msg = "This is urgent. Invest money securely."
        intelligence = self.extractor.extract(msg)
        
        self.assertIn("urgent", intelligence.keywords)
        self.assertIn("invest", intelligence.keywords)
        self.assertIn("money", intelligence.keywords)
        self.assertIn("urgent", intelligence.behavior_patterns.urgency_indicators)

if __name__ == '__main__':
    unittest.main()
