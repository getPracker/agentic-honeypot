
import sys
import os
from datetime import datetime

# Add src to sys.path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from honeypot.services.scam_detector import ScamDetector
from honeypot.services.ai_agent import AIAgent
from honeypot.models.session import Session, SessionStatus
from honeypot.models.core import Message

def test_messages():
    detector = ScamDetector()
    agent = AIAgent()
    
    test_cases = [
        {
            "name": "Lottery Scam",
            "text": "Congratulations! You won $1 million in the international lottery. Click here to claim: http://scam-win.com/claim"
        },
        # {
        #     "name": "Bank Fraud",
        #     "text": "URGENT: Your HDFC bank account is suspended due to suspicious activity. Kindly verify your KYC by providing your Account Number and OTP immediately."
        # },
        # {
        #     "name": "UPI Fraud",
        #     "text": "You have received a cashback of Rs 2000 from GPay. Scan this QR code and enter your UPI PIN to receive the money in your bank account."
        # },
        # {
        #     "name": "Investment Scam",
        #     "text": "Want to earn 50k daily? Join our VIP Crypto group. Guaranteed 200% profit in 1 week. Small investment required."
        # },
        # {
        #     "name": "Tech Support",
        #     "text": "Microsoft Security Alert! Your PC is infected with Zeus Malware. Call +1-888-000-0000 immediately for technical support."
        # },
        # {
        #     "name": "Phishing",
        #     "text": "Dear customer, your Amazon account password will expire in 2 hours. Click link to update: http://amazon-security-update.net"
        # },
        # {
        #     "name": "Clean Message",
        #     "text": "Hi Mom, I'll be home late today. Don't wait for me for dinner. See you!"
        # },
        # {
        #     "name": "Ambiguous/Business",
        #     "text": "Kindly review the attached invoice and provide the payment confirmation by tomorrow EOD. Link: https://secure.company.com/invoice/123"
        # },
        # {
        #     "name": "Safety Test (Abusive)",
        #     "text": "You are a stupid idiot and I hate you! I will bomb your house!"
        # }
    ]

    print("\n" + "="*80)
    print(f"{'MESSAGE VARIETY TEST RESULTS':^80}")
    print("="*80 + "\n")

    for case in test_cases:
        print(f"TEST CASE: {case['name']}")
        print(f"MESSAGE: \"{case['text']}\"")
        
        # 1. Analyze with Detector
        analysis = detector.analyze(case['text'])
        print(f"SCAM DETECTED: {analysis.is_scam}")
        print(f"TYPE: {analysis.scam_type.value}")
        print(f"CONFIDENCE: {analysis.confidence}")
        print(f"REASONING: {analysis.reasoning}")
        
        # 2. Generate Agent Response (using mock session)
        session = Session(
            session_id="test_session",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=SessionStatus.ACTIVE,
            messages=[]
        )
        
        # Add the message to session
        session.messages.append(Message(
            message_id="msg_1",
            sender="scammer",
            text=case['text'],
            timestamp=datetime.now()
        ))
        
        # We need to set a persona if we want better responses, 
        # but AIAgent picks one based on analysis.
        
        try:
            # Force detailed mock if no API access or just to see logic
            response = agent.generate_response(session, case['text'])
            print(f"AGENT RESPONSE: \"{response}\"")
        except Exception as e:
            print(f"AGENT ERROR: {str(e)}")
            
        print("-" * 80)

if __name__ == "__main__":
    test_messages()
