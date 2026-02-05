#!/usr/bin/env python3
"""
Test and diagnose the Vercel deployment issue
"""

import requests
import json
from datetime import datetime, timezone

# Your deployed URL
BASE_URL = "https://agentic-honeypot-chi.vercel.app"
API_KEY = "test-key-123"

def test_all_endpoints():
    """Test all possible endpoints to see what's working."""
    
    print("🔍 DIAGNOSING VERCEL DEPLOYMENT")
    print("=" * 50)
    
    endpoints_to_test = [
        "/",
        "/health", 
        "/api/v1/process-message",
        "/process",
        "/ping"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n🎯 Testing: {endpoint}")
        try:
            # Try GET first
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            print(f"GET {endpoint}: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"Response: {response.text[:200]}...")
        except Exception as e:
            print(f"GET {endpoint}: Error - {e}")
        
        # Try POST for API endpoints
        if "process" in endpoint or "api" in endpoint:
            try:
                headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
                payload = {
                    "session_id": "test",
                    "message": {
                        "sender": "scammer",
                        "text": "You won lottery!",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "message_id": "test"
                    },
                    "conversation_history": [],
                    "metadata": {"channel": "SMS", "language": "en", "locale": "en-IN"}
                }
                
                response = requests.post(f"{BASE_URL}{endpoint}", 
                                       json=payload, headers=headers, timeout=15)
                print(f"POST {endpoint}: {response.status_code}")
                if response.status_code in [200, 400, 401]:  # Any meaningful response
                    try:
                        data = response.json()
                        print(f"Response: {json.dumps(data, indent=2)[:300]}...")
                    except:
                        print(f"Response: {response.text[:300]}...")
            except Exception as e:
                print(f"POST {endpoint}: Error - {e}")

def test_with_different_payloads():
    """Test with different payload formats."""
    
    print("\n" + "=" * 50)
    print("🧪 TESTING DIFFERENT PAYLOAD FORMATS")
    print("=" * 50)
    
    # Test 1: Minimal payload
    print("\n🎯 Test 1: Minimal Payload")
    try:
        headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
        payload = {"test": "data"}
        
        response = requests.post(f"{BASE_URL}/api/v1/process-message", 
                               json=payload, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Full payload
    print("\n🎯 Test 2: Full Payload")
    try:
        headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
        payload = {
            "session_id": "vercel_test",
            "message": {
                "sender": "scammer", 
                "text": "You won 50000 rupees! Send money!",
                "timestamp": "2026-02-05T10:00:00Z",
                "message_id": "test_msg"
            },
            "conversation_history": [],
            "metadata": {
                "channel": "SMS",
                "language": "en", 
                "locale": "en-IN"
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/process-message",
                               json=payload, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! Full response:")
            print(json.dumps(data, indent=2))
            
            # Check if it's the full API or stateless mode
            if data.get("message") == "Agentic Honeypot API - Stateless Mode":
                print("\n⚠️  ISSUE: Running in stateless mode")
                print("This means the full FastAPI app isn't loading properly")
            elif "scam_detected" in data:
                print("\n✅ PERFECT: Full API is working!")
            else:
                print("\n⚠️  PARTIAL: API responding but may have issues")
        else:
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def check_vercel_routes():
    """Check what routes are configured in Vercel."""
    
    print("\n" + "=" * 50)
    print("🔧 VERCEL ROUTING ANALYSIS")
    print("=" * 50)
    
    # Check if vercel.json routes are working
    routes_to_test = [
        ("/", "Should hit api/index.py"),
        ("/health", "Should hit api/index.py"), 
        ("/ping", "Should hit api/ping.py"),
        ("/process", "Should hit api/index.py"),
        ("/api/v1/process-message", "Should hit api/index.py")
    ]
    
    for route, description in routes_to_test:
        print(f"\n🎯 {route} - {description}")
        try:
            response = requests.get(f"{BASE_URL}{route}", timeout=10)
            print(f"Status: {response.status_code}")
            
            # Check response content to see which handler it hit
            content = response.text
            if "stateless" in content.lower():
                print("→ Hitting stateless/minimal handler")
            elif "healthy" in content.lower():
                print("→ Hitting health endpoint")  
            elif "alive" in content.lower():
                print("→ Hitting ping endpoint")
            else:
                print(f"→ Unknown handler: {content[:100]}...")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_all_endpoints()
    test_with_different_payloads()
    check_vercel_routes()
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS COMPLETE")
    print("=" * 50)
    print("If you see 'stateless mode' responses, the issue is:")
    print("1. The full FastAPI app isn't loading in Vercel")
    print("2. Dependencies might be missing")
    print("3. Environment variables might not be set")
    print("4. The api/index.py might be using a fallback handler")
    print("\nCheck Vercel function logs for more details!")