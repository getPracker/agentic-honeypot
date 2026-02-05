#!/usr/bin/env python3
"""
Test the improved scam detection
"""

import requests
import json

# Test the bank threat message that was returning null
test_payload = {
    "sessionId": "1fc994e9-f4c5-47ee-8806-90aeb969928f",
    "message": {
        "sender": "scammer",
        "text": "Your bank account will be blocked today. Verify immediately.",
        "timestamp": 1769776085000
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}

def test_bank_threat():
    """Test the bank threat message."""
    
    print("🧪 Testing Improved Bank Threat Detection")
    print("=" * 50)
    
    url = "http://localhost:8000/api/v1/process-message?format=simple"
    headers = {
        "x-api-key": "test-key-123",
        "Content-Type": "application/json"
    }
    
    print(f"Message: {test_payload['message']['text']}")
    print(f"URL: {url}")
    
    try:
        response = requests.post(url, json=test_payload, headers=headers, timeout=15)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ SUCCESS!")
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            if response_data.get('reply'):
                print(f"\n🎉 AI Reply Generated: {response_data['reply']}")
                print("✅ FIXED! No more null replies!")
            else:
                print("\n❌ Still getting null reply")
                
        else:
            print("❌ FAILED!")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error: {response.text}")
                
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_bank_threat()