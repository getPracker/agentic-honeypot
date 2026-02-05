#!/usr/bin/env python3
"""
Test AI Response Generation Specifically
"""

import requests
import json
from datetime import datetime, timezone

# Configuration
API_URL = "http://localhost:8000/api/v1/process-message"
API_KEY = "test-key-123"

def test_ai_response_generation():
    """Test AI response generation with different scam types."""
    
    print("🤖 TESTING AI RESPONSE GENERATION 🤖")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Lottery Scam",
            "message": "Congratulations! You won ₹50,000 in KBC lottery! Send ₹500 to 9876543210@paytm to claim your prize!",
            "expected_engagement": True
        },
        {
            "name": "Bank Fraud",
            "message": "URGENT! Your bank account will be blocked in 24 hours. Call 9876543210 immediately to update KYC!",
            "expected_engagement": True
        },
        {
            "name": "Investment Scam",
            "message": "Invest ₹10,000 today and get ₹1,00,000 in 30 days! Guaranteed returns! Contact 9876543210",
            "expected_engagement": True
        },
        {
            "name": "UPI Fraud",
            "message": "Send ₹1000 to 9876543210@paytm for verification. Get ₹10,000 cashback instantly!",
            "expected_engagement": True
        },
        {
            "name": "Clean Message",
            "message": "Hello, how are you today? Hope you're having a great day!",
            "expected_engagement": False
        }
    ]
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎯 TEST {i}: {test_case['name']}")
        print("-" * 40)
        print(f"Message: {test_case['message'][:60]}...")
        
        payload = {
            "session_id": f"ai_test_{i}",
            "message": {
                "sender": "scammer" if test_case['expected_engagement'] else "user",
                "text": test_case['message'],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message_id": f"ai_msg_{i}"
            },
            "conversation_history": [],
            "metadata": {
                "channel": "SMS",
                "language": "en",
                "locale": "en-IN"
            }
        }
        
        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                scam_detected = data.get('scam_detected', False)
                ai_response = data.get('agent_response')
                intelligence_score = data.get('engagement_metrics', {}).get('intelligence_score', 0)
                
                print(f"✅ Status: {response.status_code}")
                print(f"📊 Scam Detected: {scam_detected}")
                print(f"📈 Intelligence Score: {intelligence_score:.2f}")
                
                if ai_response:
                    print(f"🤖 AI Response Generated: YES")
                    print(f"📝 Response Preview: {ai_response[:100]}...")
                    
                    # Check response quality
                    if len(ai_response) > 20:
                        print("✅ Response has good length")
                    else:
                        print("⚠️  Response seems short")
                        
                    # Check if response seems engaging
                    engaging_words = ['really', 'wow', 'amazing', 'confused', 'how', 'why', 'what', 'tell me', 'explain']
                    if any(word in ai_response.lower() for word in engaging_words):
                        print("✅ Response appears engaging")
                    else:
                        print("⚠️  Response may not be very engaging")
                        
                else:
                    print(f"🤖 AI Response Generated: NO")
                    if test_case['expected_engagement']:
                        print("⚠️  Expected AI response for this scam type")
                    else:
                        print("✅ Correctly no response for clean message")
                
                # Extract intelligence
                intel = data.get('extracted_intelligence', {})
                if intel.get('phone_numbers'):
                    phones = [p['number'] for p in intel['phone_numbers']]
                    print(f"📞 Extracted Phones: {phones}")
                if intel.get('upi_ids'):
                    print(f"💳 Extracted UPI: {intel['upi_ids']}")
                
                results.append({
                    'test': test_case['name'],
                    'scam_detected': scam_detected,
                    'ai_response': bool(ai_response),
                    'response_length': len(ai_response) if ai_response else 0,
                    'intelligence_score': intelligence_score,
                    'success': True
                })
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Response: {response.text}")
                results.append({
                    'test': test_case['name'],
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                'test': test_case['name'],
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 AI RESPONSE TEST SUMMARY")
    print("=" * 50)
    
    successful_tests = [r for r in results if r.get('success', False)]
    ai_responses_generated = [r for r in successful_tests if r.get('ai_response', False)]
    
    print(f"Total Tests: {len(results)}")
    print(f"Successful Requests: {len(successful_tests)}")
    print(f"AI Responses Generated: {len(ai_responses_generated)}")
    
    print("\n📊 Detailed Results:")
    for result in results:
        if result.get('success'):
            status = "✅" if result.get('ai_response') else "⭕"
            print(f"{status} {result['test']}: AI Response = {result.get('ai_response', False)}, Score = {result.get('intelligence_score', 0):.2f}")
        else:
            print(f"❌ {result['test']}: {result.get('error', 'Unknown error')}")
    
    # Final assessment
    if len(ai_responses_generated) >= 3:  # Expect at least 3 scam types to generate responses
        print(f"\n🚀 AI RESPONSE SYSTEM: WORKING CORRECTLY!")
        print(f"✅ Generated responses for {len(ai_responses_generated)} scam scenarios")
    else:
        print(f"\n⚠️  AI RESPONSE SYSTEM: May need attention")
        print(f"Only generated responses for {len(ai_responses_generated)} scenarios")

if __name__ == "__main__":
    test_ai_response_generation()