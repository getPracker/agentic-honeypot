"""
Public Deployment Test Script for Agentic Honeypot
Run this to verify your Vercel deployment.
"""

import requests
import json
import sys
from datetime import datetime
from time import sleep

# Configuration - Updated with your NEW API Key
API_KEY = "7nSdYaVoJPGXcveub_8YPhuv4hyE7G7ZeeWrfBw7Rbo"

def get_base_url():
    """Get the deployment URL from user input."""
    print("\n" + "="*70)
    print("  VERCEL DEPLOYMENT TESTER")
    print("="*70)
    print("\nEnter your Vercel URL (e.g., https://agentic-honeypot.vercel.app)")
    url = input("> ").strip().rstrip('/')
    if not url:
        print("❌ URL cannot be empty")
        sys.exit(1)
    if not url.startswith("http"):
        url = "https://" + url
    return url

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def test_health(base_url):
    url = f"{base_url}/health"
    print_header(f"Testing Health Endpoint: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ Server is healthy! (200 OK)")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def send_message(base_url, session_id, message_text, description):
    url = f"{base_url}/api/v1/process-message"
    print_header(f"Test: {description}")
    print(f"Target: {url}")
    print(f"Session: {session_id}")
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
            "locale": "en-IN"
        }
    }
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Scam Detected: {data.get('scam_detected')}")
            
            if data.get('agent_response'):
                print(f"\n🤖 AI Agent Response:\n   \"{data['agent_response']}\"")
            else:
                print("\n🤖 No AI Response (Clean message or error)")
                
            intel = data.get('extracted_intelligence', {})
            if intel:
                print("\n🔍 Extracted Intelligence:")
                if intel.get('phone_numbers'):
                    print(f"   📞 Phones: {[p['number'] for p in intel['phone_numbers']]}")
                if intel.get('upi_ids'):
                    print(f"   💳 UPI: {intel['upi_ids']}")
            return True
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    base_url = get_base_url()
    
    # 1. Health Check
    if not test_health(base_url):
        print("\n❌ Health check failed. Aborting tests.")
        return
        
    sleep(1)
    
    # 2. Lottery Scam Test
    send_message(
        base_url,
        "deploy_test_001", 
        "Congratulations! You won $1 million lottery! Call +1-555-000-0000 to claim.",
        "Lottery Scam"
    )

    print("\n✨ Test Complete!")

if __name__ == "__main__":
    main()
