#!/usr/bin/env python3
"""
Test the camelCase JSON format support
"""

import requests
import json

# Test the exact JSON format you provided
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

def test_camelcase_format():
    """Test the camelCase format."""
    
    print("🧪 Testing camelCase JSON Format")
    print("=" * 50)
    
    url = "http://localhost:8000/api/v1/process-message"
    headers = {
        "x-api-key": "test-key-123",
        "Content-Type": "application/json"
    }
    
    print("📤 Sending Request:")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(url, json=test_payload, headers=headers, timeout=15)
        
        print(f"\n📥 Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ SUCCESS! camelCase format accepted")
            print(f"Scam Detected: {response_data.get('scam_detected')}")
            if response_data.get('agent_response'):
                print(f"AI Response: {response_data['agent_response'][:100]}...")
            print(f"Intelligence Score: {response_data.get('engagement_metrics', {}).get('intelligence_score', 'N/A')}")
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
    test_camelcase_format()