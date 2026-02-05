#!/usr/bin/env python3
"""
Test both camelCase and snake_case formats
"""

import requests
import json

# Test camelCase format
camelcase_payload = {
    "sessionId": "test-camelcase-session",
    "message": {
        "sender": "scammer",
        "text": "Congratulations! You won ₹50,000 in KBC lottery!",
        "timestamp": 1769776085000
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}

# Test snake_case format
snakecase_payload = {
    "session_id": "test-snakecase-session",
    "message": {
        "sender": "scammer",
        "text": "Your bank account will be blocked today. Verify immediately.",
        "timestamp": "2026-02-05T10:00:00Z",
        "message_id": "msg_bank_test"
    },
    "conversation_history": [],
    "metadata": {
        "channel": "SMS",
        "language": "en",
        "locale": "en-IN"
    }
}

def test_format(payload, format_name):
    """Test a specific format."""
    
    print(f"\n🧪 Testing {format_name} Format")
    print("-" * 40)
    
    url = "http://localhost:8000/api/v1/process-message"
    headers = {
        "x-api-key": "test-key-123",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ {format_name} format ACCEPTED")
            print(f"Scam Detected: {response_data.get('scam_detected')}")
            print(f"Session ID: {response_data.get('session_id')}")
            
            if response_data.get('agent_response'):
                print(f"AI Response: {response_data['agent_response'][:50]}...")
            else:
                print("No AI Response (clean message)")
                
        else:
            print(f"❌ {format_name} format FAILED")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('message', 'Unknown error')}")
                if 'details' in error_data:
                    for detail in error_data['details']:
                        print(f"  - {detail.get('msg', '')} at {detail.get('loc', '')}")
            except:
                print(f"Error: {response.text}")
                
    except Exception as e:
        print(f"❌ Request failed: {e}")

def main():
    """Test both formats."""
    
    print("🔄 TESTING BOTH JSON FORMATS")
    print("=" * 50)
    
    # Test camelCase
    test_format(camelcase_payload, "camelCase")
    
    # Test snake_case
    test_format(snakecase_payload, "snake_case")
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print("Both formats should work now!")

if __name__ == "__main__":
    main()