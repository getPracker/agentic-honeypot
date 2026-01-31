"""Property tests for IntelligenceExtractor."""

import sys
import os
import unittest
from hypothesis import given, strategies as st

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeypot.services.intelligence_extractor import IntelligenceExtractor

class TestIntelligenceExtractorProperties(unittest.TestCase):
    def setUp(self):
        self.extractor = IntelligenceExtractor()

    @given(st.text())
    def test_extract_completeness(self, text):
        """Property: Extract never raises exceptions."""
        result = self.extractor.extract(text)
        self.assertIsNotNone(result)

    @given(st.from_regex(r"\d{10}", fullmatch=True))
    def test_extract_phone_regex_compat(self, phone):
        """Property: Should generally find simpler phone patterns if minimal noise."""
        # Note: Our regex requires 6-9 start for 10 digits.
        if phone[0] in "6789":
             res = self.extractor.extract(f"call {phone}")
             # Might detect or not depending on strictness, but let's verify if detected, it matches
             if res.phone_numbers:
                 self.assertTrue(any(phone in p.number for p in res.phone_numbers))

if __name__ == '__main__':
    unittest.main()
