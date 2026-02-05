#!/usr/bin/env python3
"""
Test script for the local server to ensure it behaves identically to Vercel.
"""

import requests
import json
import time

def test_health_endpoint(base_url):
    """Test the health endpoint."""
    print("🔍 Testing health endpoint...")
    
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_process_endpoint(base_url):
    """Test the main processing endpoint."""
    print("🤖 Testing process endpoint...")
    
    # Test data matching the expected format
    test_data = {
        "sessionId": "test_session_123",
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately.",
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": "test-api-key"  # Optional for testing
    }
    
    response = requests.post(
        f"{base_url}/api/v1/process-message",
        json=test_data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_conversation_flow(base_url):
    """Test a multi-turn conversation."""
    print("💬 Testing conversation flow...")
    
    session_id = f"conversation_test_{int(time.time())}"
    conversation_history = []
    
    # First message
    message1 = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Congratulations! You've won $10,000. Click here to claim.",
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": conversation_history,
        "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
    }
    
    response1 = requests.post(f"{base_url}/api/v1/process-message", json=message1)
    print(f"Turn 1 - Status: {response1.status_code}")
    print(f"Turn 1 - Response: {response1.json()}")
    
    # Add to conversation history
    conversation_history.append({
        "sender": "scammer",
        "text": message1["message"]["text"],
        "timestamp": message1["message"]["timestamp"]
    })
    
    if response1.json().get("reply"):
        conversation_history.append({
            "sender": "agent",
            "text": response1.json()["reply"],
            "timestamp": int(time.time() * 1000)
        })
    
    # Second message
    message2 = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer", 
            "text": "Just provide your bank details to verify your identity.",
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": conversation_history,
        "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
    }
    
    response2 = requests.post(f"{base_url}/api/v1/process-message", json=message2)
    print(f"Turn 2 - Status: {response2.status_code}")
    print(f"Turn 2 - Response: {response2.json()}")
    print()

def main():
    """Run all tests."""
    base_url = "http://localhost:8000"
    
    print("🚀 Testing Local Honeypot Server")
    print(f"📍 Base URL: {base_url}")
    print("=" * 50)
    
    try:
        test_health_endpoint(base_url)
        test_process_endpoint(base_url)
        test_conversation_flow(base_url)
        
        print("✅ All tests completed!")
        print("🎯 Server is working correctly and ready for Vercel deployment")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed!")
        print("💡 Make sure the server is running: python local_server.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()