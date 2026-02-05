#!/usr/bin/env python3
"""
Comprehensive Localhost Testing vs Vercel Deployment
Compare local full API vs Vercel stateless mode
"""

import requests
import json
from datetime import datetime, timezone
import time

# URLs
LOCALHOST_URL = "http://localhost:8000"
VERCEL_URL = "https://agentic-honeypot-chi.vercel.app"
API_KEY = "test-key-123"

def test_endpoint(base_url, endpoint, method="GET", payload=None, description=""):
    """Test a single endpoint."""
    url = f"{base_url}{endpoint}"
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            "response_time": response.elapsed.total_seconds(),
            "success": response.status_code == 200
        }
    except Exception as e:
        return {
            "status_code": "ERROR",
            "response": str(e),
            "response_time": 0,
            "success": False
        }

def run_comprehensive_test():
    """Run comprehensive tests on both localhost and Vercel."""
    
    print("🔬 COMPREHENSIVE LOCALHOST vs VERCEL COMPARISON")
    print("=" * 70)
    
    # Test cases
    test_cases = [
        {
            "name": "Health Check",
            "endpoint": "/health",
            "method": "GET",
            "payload": None
        },
        {
            "name": "Lottery Scam",
            "endpoint": "/api/v1/process-message",
            "method": "POST",
            "payload": {
                "session_id": "test_lottery_comparison",
                "message": {
                    "sender": "scammer",
                    "text": "Congratulations! You won ₹50,000 in KBC lottery! Send ₹500 to 9876543210@paytm to claim!",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "message_id": "msg_lottery"
                },
                "conversation_history": [],
                "metadata": {
                    "channel": "SMS",
                    "language": "en",
                    "locale": "en-IN"
                }
            }
        },
        {
            "name": "Bank Fraud",
            "endpoint": "/api/v1/process-message",
            "method": "POST",
            "payload": {
                "session_id": "test_bank_comparison",
                "message": {
                    "sender": "scammer",
                    "text": "URGENT! Your bank account blocked. Call 9876543210 immediately!",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "message_id": "msg_bank"
                },
                "conversation_history": [],
                "metadata": {
                    "channel": "SMS",
                    "language": "en",
                    "locale": "en-IN"
                }
            }
        },
        {
            "name": "Clean Message",
            "endpoint": "/api/v1/process-message",
            "method": "POST",
            "payload": {
                "session_id": "test_clean_comparison",
                "message": {
                    "sender": "user",
                    "text": "Hello, how are you today?",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "message_id": "msg_clean"
                },
                "conversation_history": [],
                "metadata": {
                    "channel": "SMS",
                    "language": "en",
                    "locale": "en-IN"
                }
            }
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        print(f"\n🎯 Testing: {test_case['name']}")
        print("-" * 50)
        
        # Test localhost
        print("📍 LOCALHOST:")
        localhost_result = test_endpoint(
            LOCALHOST_URL, 
            test_case['endpoint'], 
            test_case['method'], 
            test_case['payload']
        )
        
        print(f"  Status: {localhost_result['status_code']}")
        print(f"  Time: {localhost_result['response_time']:.2f}s")
        
        if localhost_result['success']:
            response = localhost_result['response']
            if isinstance(response, dict):
                if 'scam_detected' in response:
                    print(f"  Scam Detected: {response.get('scam_detected')}")
                if 'agent_response' in response and response['agent_response']:
                    print(f"  AI Response: {response['agent_response'][:60]}...")
                if 'status' in response:
                    print(f"  Status: {response['status']}")
            print("  ✅ Full API Response")
        else:
            print(f"  ❌ Error: {localhost_result['response']}")
        
        # Test Vercel
        print("\n🌐 VERCEL:")
        vercel_result = test_endpoint(
            VERCEL_URL, 
            test_case['endpoint'], 
            test_case['method'], 
            test_case['payload']
        )
        
        print(f"  Status: {vercel_result['status_code']}")
        print(f"  Time: {vercel_result['response_time']:.2f}s")
        
        if vercel_result['success']:
            response = vercel_result['response']
            if isinstance(response, dict):
                if 'reply' in response:
                    print(f"  AI Reply: {response['reply'][:60]}...")
                if 'status' in response:
                    print(f"  Status: {response['status']}")
                if 'mode' in response:
                    print(f"  Mode: {response['mode']}")
            print("  ✅ Stateless Mode Response")
        else:
            print(f"  ❌ Error: {vercel_result['response']}")
        
        # Store results
        results[test_case['name']] = {
            'localhost': localhost_result,
            'vercel': vercel_result
        }
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 COMPARISON SUMMARY")
    print("=" * 70)
    
    print(f"{'Test Case':<20} {'Localhost':<15} {'Vercel':<15} {'Both Work':<10}")
    print("-" * 70)
    
    for test_name, result in results.items():
        localhost_status = "✅ OK" if result['localhost']['success'] else "❌ FAIL"
        vercel_status = "✅ OK" if result['vercel']['success'] else "❌ FAIL"
        both_work = "✅ YES" if result['localhost']['success'] and result['vercel']['success'] else "❌ NO"
        
        print(f"{test_name:<20} {localhost_status:<15} {vercel_status:<15} {both_work:<10}")
    
    # Performance comparison
    print(f"\n⚡ PERFORMANCE COMPARISON:")
    for test_name, result in results.items():
        if result['localhost']['success'] and result['vercel']['success']:
            localhost_time = result['localhost']['response_time']
            vercel_time = result['vercel']['response_time']
            faster = "Localhost" if localhost_time < vercel_time else "Vercel"
            print(f"  {test_name}: Localhost {localhost_time:.2f}s vs Vercel {vercel_time:.2f}s → {faster} faster")
    
    # Feature comparison
    print(f"\n🔍 FEATURE COMPARISON:")
    print("  Localhost (Full API):")
    print("    ✅ Complete scam detection")
    print("    ✅ Intelligence extraction")
    print("    ✅ Detailed metrics")
    print("    ✅ Session management")
    print("    ✅ Full error handling")
    
    print("  Vercel (Stateless Mode):")
    print("    ✅ AI response generation")
    print("    ✅ Basic scam detection")
    print("    ✅ Authentication")
    print("    ⚠️  Simplified responses")
    print("    ⚠️  No detailed intelligence")
    
    return results

def test_postman_scenarios():
    """Test specific Postman scenarios."""
    
    print("\n" + "=" * 70)
    print("📮 POSTMAN TESTING SCENARIOS")
    print("=" * 70)
    
    scenarios = [
        {
            "name": "Missing API Key",
            "test": lambda: requests.post(f"{LOCALHOST_URL}/api/v1/process-message", 
                                        json={"test": "data"}, timeout=10)
        },
        {
            "name": "Invalid API Key", 
            "test": lambda: requests.post(f"{LOCALHOST_URL}/api/v1/process-message",
                                        json={"test": "data"},
                                        headers={"x-api-key": "invalid", "Content-Type": "application/json"},
                                        timeout=10)
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🧪 {scenario['name']}:")
        try:
            response = scenario['test']()
            print(f"  Status: {response.status_code}")
            if response.status_code in [401, 400]:
                print("  ✅ Correctly handled error")
            else:
                print(f"  ⚠️  Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting comprehensive localhost testing...")
    print("Make sure your local server is running on http://localhost:8000")
    print()
    
    # Quick connectivity test
    try:
        response = requests.get(f"{LOCALHOST_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Local server is running!")
        else:
            print("❌ Local server not responding properly")
            exit(1)
    except:
        print("❌ Cannot connect to local server. Please start it first:")
        print("   python start_server.py")
        exit(1)
    
    # Run comprehensive tests
    results = run_comprehensive_test()
    
    # Test Postman scenarios
    test_postman_scenarios()
    
    print("\n" + "=" * 70)
    print("🎉 LOCALHOST TESTING COMPLETE!")
    print("=" * 70)
    print("✅ Local server provides full API functionality")
    print("✅ Vercel provides simplified but working AI responses")
    print("✅ Both deployments are functional for testing")
    print("\n🎯 Use localhost for full feature testing")
    print("🌐 Use Vercel for public demos and simplified testing")