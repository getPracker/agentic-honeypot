#!/usr/bin/env python3
"""
Test the Vercel deployed Agentic Honeypot API
"""

import requests
import json
from datetime import datetime, timezone

# Your deployed URL
API_URL = "https://agentic-honeypot-chi.vercel.app/api/v1/process-message"
HEALTH_URL = "https://agentic-honeypot-chi.vercel.app/health"
API_KEY = "test-key-123"

def test_deployment():
    """Test the deployed API."""
    
    print("🌐 TESTING VERCEL DEPLOYMENT")
    print("=" * 50)
    print(f"URL: https://agentic-honeypot-chi.vercel.app/")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n🏥 Testing Health Endpoint...")
    try:
        response = requests.get(HEALTH_URL, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code == 200:
            print("✅ Health check passed!")
        else:
            print("❌ Health check failed!")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: API Endpoint
    print("\n🎯 Testing Main API Endpoint...")
    
    payload = {
        "session_id": "vercel_test_001",
        "message": {
            "sender": "scammer",
            "text": "Congratulations! You won ₹50,000 in KBC lottery! Send ₹500 to 9876543210@paytm to claim your prize!",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message_id": "vercel_msg_001"
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
        print("Sending request...")
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API request successful!")
            print(f"Scam Detected: {data.get('scam_detected', 'N/A')}")
            print(f"Status: {data.get('status', 'N/A')}")
            
            if data.get('agent_response'):
                print(f"🤖 AI Response: {data['agent_response'][:100]}...")
            else:
                print("🤖 AI Response: None")
            
            intel = data.get('extracted_intelligence', {})
            if intel:
                print("\n🔍 Extracted Intelligence:")
                if intel.get('phone_numbers'):
                    phones = [p.get('number', p) if isinstance(p, dict) else p for p in intel['phone_numbers']]
                    print(f"  📞 Phone Numbers: {phones}")
                if intel.get('upi_ids'):
                    print(f"  💳 UPI IDs: {intel['upi_ids']}")
            
            print("\n🎉 DEPLOYMENT IS WORKING!")
            return True
            
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (this is common with serverless cold starts)")
        print("Try again - serverless functions need warm-up time")
        return False
    except Exception as e:
        print(f"❌ API request error: {e}")
        return False

def test_error_cases():
    """Test error handling."""
    print("\n🔐 Testing Error Cases...")
    
    # Test without API key
    try:
        response = requests.post(API_URL, json={"test": "data"}, timeout=10)
        if response.status_code == 401:
            print("✅ Correctly rejected request without API key")
        else:
            print(f"⚠️  Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"⚠️  Error test failed: {e}")

if __name__ == "__main__":
    success = test_deployment()
    test_error_cases()
    
    if success:
        print("\n" + "=" * 50)
        print("🚀 READY FOR POSTMAN TESTING!")
        print("Use these details in Postman:")
        print(f"Base URL: https://agentic-honeypot-chi.vercel.app")
        print(f"API Key: {API_KEY}")
        print("=" * 50)
    else:
        print("\n❌ Deployment may have issues. Check Vercel logs.")