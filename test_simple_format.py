#!/usr/bin/env python3
"""
Test the new simple response format
"""

import requests
import json

# Test payload
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

def test_format(format_type):
    """Test a specific response format."""
    
    print(f"\n🧪 Testing {format_type.upper()} Format")
    print("-" * 50)
    
    # Add format query parameter
    url = f"http://localhost:8000/api/v1/process-message?format={format_type}"
    headers = {
        "x-api-key": "test-key-123",
        "Content-Type": "application/json"
    }
    
    print(f"URL: {url}")
    print(f"Message: {test_payload['message']['text']}")
    
    try:
        response = requests.post(url, json=test_payload, headers=headers, timeout=15)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ {format_type.upper()} format SUCCESS")
            print(f"Response: {json.dumps(response_data, indent=2)}")
        else:
            print(f"❌ {format_type.upper()} format FAILED")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error: {response.text}")
                
    except Exception as e:
        print(f"❌ Request failed: {e}")

def main():
    """Test both response formats."""
    
    print("🔄 TESTING RESPONSE FORMATS")
    print("=" * 60)
    
    # Test full format (default)
    test_format("full")
    
    # Test simple format (what you want)
    test_format("simple")
    
    print("\n" + "=" * 60)
    print("🎯 USAGE:")
    print("For simple format: Add ?format=simple to your URL")
    print("For full format: Use default URL or ?format=full")

if __name__ == "__main__":
    main()