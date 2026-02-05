#!/usr/bin/env python3
"""
Test camelCase format with obvious scam message
"""

import requests
import json

# Test with obvious scam message
test_payload = {
    "sessionId": "1fc994e9-f4c5-47ee-8806-90aeb969928f",
    "message": {
        "sender": "scammer",
        "text": "Congratulations! You won ₹50,000 in KBC lottery! Send ₹500 to 9876543210@paytm to claim your prize immediately!",
        "timestamp": 1769776085000
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}

def test_camelcase_scam():
    """Test camelCase format with obvious scam."""
    
    print("🎯 Testing camelCase with Obvious Scam")
    print("=" * 50)
    
    url = "http://localhost:8000/api/v1/process-message"
    headers = {
        "x-api-key": "test-key-123",
        "Content-Type": "application/json"
    }
    
    print("📤 Sending Lottery Scam (camelCase):")
    print(f"Message: {test_payload['message']['text']}")
    
    try:
        response = requests.post(url, json=test_payload, headers=headers, timeout=15)
        
        print(f"\n📥 Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ SUCCESS! camelCase format accepted")
            print(f"Scam Detected: {response_data.get('scam_detected')}")
            print(f"Intelligence Score: {response_data.get('engagement_metrics', {}).get('intelligence_score', 'N/A')}")
            
            if response_data.get('agent_response'):
                print(f"AI Response: {response_data['agent_response'][:100]}...")
                print("✅ AI Response Generated!")
            else:
                print("❌ No AI Response Generated")
                
            # Check extracted intelligence
            intelligence = response_data.get('extracted_intelligence', {})
            if intelligence.get('phone_numbers'):
                print(f"📞 Extracted Phones: {intelligence['phone_numbers']}")
            if intelligence.get('upi_ids'):
                print(f"💳 Extracted UPI: {intelligence['upi_ids']}")
                
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
    test_camelcase_scam()