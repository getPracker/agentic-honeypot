"""
Quick Test Script for Agentic Honeypot
Run this after starting the server to verify everything works.
"""

import requests
import json
from datetime import datetime
from time import sleep

# Configuration
API_URL = "http://localhost:8000/api/v1/process-message"
HEALTH_URL = "http://localhost:8000/health"
API_KEY = "test-key-123"

def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def test_health():
    """Test if the server is running."""
    print_header("Testing Server Health")
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("\nStart the server with:")
        print("  $env:PYTHONPATH='src'")
        print("  python -m uvicorn honeypot.main:create_app --factory --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def send_message(session_id, message_text, description):
    """Send a test message to the honeypot."""
    print_header(f"Test: {description}")
    print(f"Session ID: {session_id}")
    print(f"Message: {message_text}\n")
    
    payload = {
        "session_id": session_id,
        "message": {
            "sender": "scammer",
            "text": message_text,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message_id": f"msg_{int(datetime.utcnow().timestamp())}"
        },
        "conversation_history": [],
        "metadata": {
            "channel": "SMS",
            "language": "en",
            "locale": "en-IN",
            "source_ip": "192.168.1.100"
        }
    }
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Scam Detected: {data.get('scam_detected', False)}")
            
            if data.get('agent_response'):
                print(f"\n🤖 AI Agent Response:")
                print(f"   {data['agent_response']}")
            
            intel = data.get('extracted_intelligence', {})
            if intel:
                print(f"\n🔍 Extracted Intelligence:")
                if intel.get('phone_numbers'):
                    print(f"   📞 Phone Numbers: {[p['number'] for p in intel['phone_numbers']]}")
                if intel.get('upi_ids'):
                    print(f"   💳 UPI IDs: {intel['upi_ids']}")
                if intel.get('bank_accounts'):
                    print(f"   🏦 Bank Accounts: {[b['account_number'] for b in intel['bank_accounts']]}")
                if intel.get('keywords'):
                    print(f"   🔑 Keywords: {intel['keywords'][:5]}")  # Show first 5
            
            metrics = data.get('engagement_metrics', {})
            if metrics:
                print(f"\n📊 Metrics:")
                print(f"   Messages: {metrics.get('message_count', 0)}")
                print(f"   Intelligence Score: {metrics.get('intelligence_score', 0):.2f}")
            
            return data
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (AI might be slow, try again)")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Run all tests."""
    print("\n" + "🍯" * 35)
    print("  AGENTIC HONEYPOT - QUICK TEST SUITE")
    print("🍯" * 35)
    
    # Test 1: Health Check
    if not test_health():
        print("\n⚠️  Server is not running. Please start it first.")
        return
    
    sleep(1)
    
    # Test 2: Lottery Scam
    send_message(
        "test_lottery_001",
        "Congratulations! You won ₹50,000 in KBC lottery! Send ₹500 to 9876543210@paytm to claim your prize!",
        "Lottery Scam Detection"
    )
    
    sleep(2)
    
    # Test 3: Bank Fraud
    send_message(
        "test_bank_001",
        "URGENT! Your bank account will be blocked in 24 hours. Update KYC by calling 9876543210 immediately!",
        "Bank Fraud Detection"
    )
    
    sleep(2)
    
    # Test 4: Investment Scam
    send_message(
        "test_investment_001",
        "Invest ₹10,000 today and get ₹1,00,000 in 30 days! Guaranteed returns! Transfer to account 1234567890 IFSC SBIN0001234",
        "Investment Scam with Bank Details"
    )
    
    sleep(2)
    
    # Test 5: Clean Message (should not engage)
    send_message(
        "test_clean_001",
        "Hello, how are you doing today? Hope you're having a great day!",
        "Clean Message (No Scam)"
    )
    
    # Summary
    print_header("Test Summary")
    print("✅ All tests completed!")
    print("\nWhat to check:")
    print("  1. Scam messages should be detected (scam_detected: true)")
    print("  2. AI should respond to scams (agent_response present)")
    print("  3. Intelligence should be extracted (phone numbers, UPI IDs, etc.)")
    print("  4. Clean messages should NOT get AI responses")
    print("\n📝 Check the server logs for detailed processing information")
    print("📊 Check GUVI callback endpoint for reported data\n")

if __name__ == "__main__":
    main()
