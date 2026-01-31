# Testing Guide - Agentic Honeypot

## Quick Start Testing

### 1. Start the Server

```powershell
# Navigate to project directory
cd c:\Users\Sahil\Downloads\agentic-honeypot-main\agentic-honeypot-main

# Set Python path
$env:PYTHONPATH='src'

# Start the FastAPI server
python -m uvicorn honeypot.main:create_app --factory --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2. Test Health Check

Open browser or use curl:
```powershell
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "service": "agentic-honeypot"
}
```

---

## Testing Methods

### Method 1: Using PowerShell (Recommended)

Create a test script `test_honeypot.ps1`:

```powershell
# Test 1: Lottery Scam
$body = @{
    session_id = "test_lottery_001"
    message = @{
        sender = "scammer"
        text = "Congratulations! You won ₹50,000 in KBC lottery! Send ₹500 to 9876543210@paytm to claim. Call 9876543210"
        timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        message_id = "msg_001"
    }
    conversation_history = @()
    metadata = @{
        channel = "SMS"
        language = "en"
        locale = "en-IN"
        source_ip = "192.168.1.100"
    }
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/process-message" `
    -Method Post `
    -Headers @{"x-api-key"="test-key-123"; "Content-Type"="application/json"} `
    -Body $body

$response | ConvertTo-Json -Depth 10
```

Run it:
```powershell
.\test_honeypot.ps1
```

### Method 2: Using Python Script

Create `test_api.py`:

```python
import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000/api/v1/process-message"
API_KEY = "test-key-123"

def test_scam_message(session_id, message_text):
    """Test the honeypot with a scam message."""
    
    payload = {
        "session_id": session_id,
        "message": {
            "sender": "scammer",
            "text": message_text,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message_id": f"msg_{int(datetime.utcnow().timestamp())}"
        },
        "conversation_history": [],
        "metadata": {
            "channel": "SMS",
            "language": "en",
            "locale": "en-IN",
            "source_ip": "192.168.1.100"
        }
    }
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    response = requests.post(API_URL, json=payload, headers=headers)
    
    print(f"\n{'='*60}")
    print(f"Test: {session_id}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse:")
    print(json.dumps(response.json(), indent=2))
    
    return response.json()

# Test Cases
if __name__ == "__main__":
    # Test 1: Lottery Scam
    test_scam_message(
        "lottery_scam_001",
        "Congratulations! You won ₹50,000 in KBC lottery! Send ₹500 to 9876543210@paytm"
    )
    
    # Test 2: Bank Fraud
    test_scam_message(
        "bank_fraud_001",
        "Your bank account has been blocked! Update KYC immediately. Send details to 9876543210"
    )
    
    # Test 3: Investment Scam
    test_scam_message(
        "investment_001",
        "Invest ₹10,000 and get ₹1,00,000 in 30 days! Guaranteed returns! Contact 9876543210"
    )
    
    # Test 4: Clean Message (should not engage)
    test_scam_message(
        "clean_001",
        "Hello, how are you today?"
    )
```

Run it:
```powershell
python test_api.py
```

### Method 3: Using Postman

1. **Import Collection**: Create a new request
2. **URL**: `http://localhost:8000/api/v1/process-message`
3. **Method**: POST
4. **Headers**:
   - `x-api-key`: `test-key-123`
   - `Content-Type`: `application/json`
5. **Body** (raw JSON):
```json
{
  "session_id": "postman_test_001",
  "message": {
    "sender": "scammer",
    "text": "You won lottery! Send money to 9876543210@paytm",
    "timestamp": "2026-01-28T15:56:00Z",
    "message_id": "msg_001"
  },
  "conversation_history": [],
  "metadata": {
    "channel": "SMS",
    "language": "en",
    "locale": "en-IN"
  }
}
```

---

## Test Scenarios

### Scenario 1: Lottery Scam Detection

**Input**:
```
"Congratulations! You've won ₹50,000 in the KBC lottery! 
Send ₹500 processing fee to claim your prize."
```

**Expected Output**:
- ✅ `scam_detected`: `true`
- ✅ `scam_type`: `FAKE_OFFER`
- ✅ `confidence`: > 0.8
- ✅ `agent_response`: Engaging response from AI
- ✅ `extracted_intelligence`: Contains keywords

### Scenario 2: Bank Fraud Detection

**Input**:
```
"Your bank account will be blocked in 24 hours! 
Update your KYC details immediately by calling 9876543210"
```

**Expected Output**:
- ✅ `scam_detected`: `true`
- ✅ `scam_type`: `BANK_FRAUD`
- ✅ `extracted_intelligence.phone_numbers`: `["9876543210"]`
- ✅ `behavior_patterns.urgency_indicators`: Present

### Scenario 3: UPI Fraud Detection

**Input**:
```
"Send ₹1000 to 9876543210@paytm for verification. 
You'll get ₹10,000 cashback!"
```

**Expected Output**:
- ✅ `scam_detected`: `true`
- ✅ `extracted_intelligence.upi_ids`: `["9876543210@paytm"]`
- ✅ `extracted_intelligence.keywords`: Contains "cashback"

### Scenario 4: Multi-turn Conversation

**Turn 1**:
```json
{
  "session_id": "conversation_001",
  "message": {
    "text": "You won lottery! Call 9876543210"
  }
}
```

**Turn 2** (use same session_id):
```json
{
  "session_id": "conversation_001",
  "message": {
    "text": "Send money to account 1234567890 IFSC SBIN0001234"
  }
}
```

**Expected**:
- ✅ Session maintains history
- ✅ Intelligence accumulates (phone + bank account)
- ✅ AI responses build on conversation

### Scenario 5: Clean Message (No Scam)

**Input**:
```
"Hello, how are you doing today?"
```

**Expected Output**:
- ✅ `scam_detected`: `false`
- ✅ `agent_response`: `null` (no engagement)
- ✅ `extracted_intelligence`: Empty or minimal

---

## Interactive Testing

### Using Interactive Python Shell

```python
import sys
sys.path.insert(0, 'src')

from honeypot.services.scam_detector import ScamDetector
from honeypot.services.intelligence_extractor import IntelligenceExtractor
from honeypot.services.ai_agent import AIAgent

# Test Scam Detection
detector = ScamDetector()
result = detector.analyze("You won lottery! Send money!")
print(f"Scam: {result.is_scam}, Confidence: {result.confidence}")

# Test Intelligence Extraction
extractor = IntelligenceExtractor()
intel = extractor.extract("Call 9876543210 or send to 1234567890@paytm")
print(f"Phone: {intel.phone_numbers}")
print(f"UPI: {intel.upi_ids}")

# Test AI Agent (requires API key)
agent = AIAgent()
# Note: Will use mock responses if no API key configured
```

---

## Running Automated Tests

### Run All Tests
```powershell
$env:PYTHONPATH='src'
python -m pytest tests -v
```

### Run Specific Test Files
```powershell
# Test scam detection
python -m pytest tests/test_scam_detector.py -v

# Test AI agent
python -m pytest tests/test_ai_agent.py -v

# Test orchestrator
python -m pytest tests/test_orchestrator.py -v

# Test encryption
python -m pytest tests/test_encryption.py -v
```

### Run with Coverage
```powershell
pip install pytest-cov
python -m pytest tests --cov=honeypot --cov-report=html
```

---

## Expected Responses

### Successful Scam Detection Response

```json
{
  "status": "success",
  "scam_detected": true,
  "agent_response": "Wow, really? I won money? That's amazing! But I'm confused, why do I need to send money first?",
  "engagement_metrics": {
    "conversation_duration": 0,
    "message_count": 2,
    "engagement_quality": 0.8,
    "intelligence_score": 0.6
  },
  "extracted_intelligence": {
    "bank_accounts": [],
    "upi_ids": ["9876543210@paytm"],
    "phone_numbers": [
      {
        "number": "9876543210",
        "context": "Call 9876543210",
        "confidence": 0.9
      }
    ],
    "urls": [],
    "keywords": ["won", "lottery", "send", "money"],
    "behavior_patterns": {
      "urgency_indicators": ["Congratulations"],
      "financial_requests": ["Send money"],
      "coercion_tactics": []
    }
  },
  "agent_notes": "Lottery scam with payment request",
  "session_id": "test_lottery_001"
}
```

### Error Response (Missing API Key)

```json
{
  "status": "error",
  "message": "Invalid or missing API key",
  "error_code": "AUTHENTICATION_ERROR"
}
```

---

## Troubleshooting

### Issue: "Module not found"
**Solution**:
```powershell
$env:PYTHONPATH='src'
```

### Issue: "Invalid API key"
**Solution**: Check `.env` file has `API_KEYS=["test-key-123"]`

### Issue: "Encryption key error"
**Solution**: Ensure `.env` has valid Fernet key:
```
ENCRYPTION_KEY=DGRP2s9PsfDib7V9rKaa4Dld-DfTaqPiCkIJ3Y1EOWQ=
```

### Issue: "No AI response"
**Solution**: 
- Check if Gemini API key is set in `.env`
- System will use mock responses if no API key
- Verify `DEFAULT_LLM_PROVIDER=gemini`

---

## Performance Testing

### Load Test with Multiple Requests

```python
import concurrent.futures
import requests

def send_request(i):
    payload = {
        "session_id": f"load_test_{i}",
        "message": {
            "sender": "scammer",
            "text": "You won lottery!",
            "timestamp": "2026-01-28T15:56:00Z",
            "message_id": f"msg_{i}"
        },
        "conversation_history": [],
        "metadata": {"channel": "SMS", "language": "en", "locale": "en-IN"}
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/process-message",
        json=payload,
        headers={"x-api-key": "test-key-123"}
    )
    return response.status_code

# Send 100 concurrent requests
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(send_request, range(100)))

print(f"Success rate: {results.count(200)}/100")
```

---

## Next Steps

1. ✅ Start the server
2. ✅ Test health endpoint
3. ✅ Run a simple scam detection test
4. ✅ Try multi-turn conversation
5. ✅ Check callback logs (if GUVI endpoint is live)
6. ✅ Run automated test suite

**The honeypot is ready for testing! 🎯**
