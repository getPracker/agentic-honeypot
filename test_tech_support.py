
import sys
import os
from datetime import datetime

# Add src to sys.path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from honeypot.services.scam_detector import ScamDetector

def test_tech_support():
    detector = ScamDetector()
    text = "Microsoft Security Alert! Your PC is infected with Zeus Malware. Call +1-888-000-0000 immediately for technical support."
    analysis = detector.analyze(text)
    print(f"CASE: Tech Support")
    print(f"MESSAGE: {text}")
    print(f"SCAM DETECTED: {analysis.is_scam}")
    print(f"TYPE: {analysis.scam_type.value}")
    print(f"CONFIDENCE: {analysis.confidence}")
    print(f"INDICATORS: {analysis.risk_indicators}")

if __name__ == "__main__":
    test_tech_support()
