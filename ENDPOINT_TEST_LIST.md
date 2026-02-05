# Agentic Honeypot - API Endpoint Test List

## 🚀 Base Configuration

**Base URL:** `http://localhost:8000`  
**API Key:** `test-key-123` (from .env file)  
**Content-Type:** `application/json`  
**Authentication:** Header `x-api-key`

---

## 📋 Available Endpoints

### 1. Health Check Endpoint
### 2. Message Processing Endpoint
### 3. Ping Endpoint (Serverless)

---

## 🧪 Test Cases

### **1. Health Check Endpoint**

#### **GET /health**

**Purpose:** Verify server is running and healthy

**Test Case 1.1: Basic Health Check**
```bash
curl -X GET "http://localhost:8000/health"
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "agentic-honeypot"
}
```

**Status Code:** `200 OK`

---

### **2. Message Processing Endpoint**

#### **POST /api/v1/process-message**

**Purpose:** Process messages for scam detection and intelligence extraction

#### **Test Case 2.1: Lottery Scam Detection**
```bash
curl -X POST "http://localhost:8000/api/v1/process-message" \
  -H "x-api-key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_lottery_001",
    "message": {
      "sender": "scammer",
      "text": "Congratulations! You won ₹50,000 in KBC lottery! Send ₹500 to 9876543210@paytm to claim your prize!",
      "timestamp": "2026-02-05T15:30:00Z",
      "message_id": "msg_001"
    },
    "conversation_history": [],
    "metadata": {
      "channel": "SMS",
      "language": "en",
      "locale": "en-IN",
      "source_ip": "192.168.1.100"
    }
  }'
```

**Expected Response:**
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
        "country_code": "+91",
        "is_verified": false,
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

#### **Test Case 2.2: Bank Fraud Detection**
```bash
curl -X POST "http://localhost:8000/api/v1/process-message" \
  -H "x-api-key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_bank_001",
    "message": {
      "sender": "scammer",
      "text": "URGENT! Your bank account will be blocked in 24 hours. Update KYC by calling 9876543210 immediately!",
      "timestamp": "2026-02-05T15:30:00Z",
      "message_id": "msg_002"
    },
    "conversation_history": [],
    "metadata": {
      "channel": "SMS",
      "language": "en",
      "locale": "en-IN"
    }
  }'
```

#### **Test Case 2.3: Investment Scam with Bank Details**
```bash
curl -X POST "http://localhost:8000/api/v1/process-message" \
  -H "x-api-key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_investment_001",
    "message": {
      "sender": "scammer",
      "text": "Invest ₹10,000 today and get ₹1,00,000 in 30 days! Guaranteed returns! Transfer to account 1234567890 IFSC SBIN0001234",
      "timestamp": "2026-02-05T15:30:00Z",
      "message_id": "msg_003"
    },
    "conversation_history": [],
    "metadata": {
      "channel": "WhatsApp",
      "language": "en",
      "locale": "en-IN"
    }
  }'
```

#### **Test Case 2.4: UPI Fraud**
```bash
curl -X POST "http://localhost:8000/api/v1/process-message" \
  -H "x-api-key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_upi_001",
    "message": {
      "sender": "scammer",
      "text": "Send ₹1000 to 9876543210@paytm for verification. You will get ₹10,000 cashback instantly!",
      "timestamp": "2026-02-05T15:30:00Z",
      "message_id": "msg_004"
    },
    "conversation_history": [],
    "metadata": {
      "channel": "SMS",
      "language": "en",
      "locale": "en-IN"
    }
  }'
```

#### **Test Case 2.5: Clean Message (No Scam)**
```bash
curl -X POST "http://localhost:8000/api/v1/process-message" \
  -H "x-api-key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_clean_001",
    "message": {
      "sender": "user",
      "text": "Hello, how are you doing today? Hope you are having a great day!",
      "timestamp": "2026-02-05T15:30:00Z",
      "message_id": "msg_005"
    },
    "conversation_history": [],
    "metadata": {
      "channel": "SMS",
      "language": "en",
      "locale": "en-IN"
    }
  }'
```

**Expected Response for Clean Message:**
```json
{
  "status": "success",
  "scam_detected": false,
  "agent_response": null,
  "engagement_metrics": {
    "conversation_duration": 0,
    "message_count": 1,
    "engagement_quality": 0.0,
    "intelligence_score": 0.0
  },
  "extracted_intelligence": {
    "bank_accounts": [],
    "upi_ids": [],
    "phone_numbers": [],
    "urls": [],
    "keywords": [],
    "behavior_patterns": {
      "urgency_indicators": [],
      "financial_requests": [],
      "coercion_tactics": []
    }
  },
  "agent_notes": "",
  "session_id": "test_clean_001"
}
```

#### **Test Case 2.6: Multi-turn Conversation**
```bash
# First message
curl -X POST "http://localhost:8000/api/v1/process-message" \
  -H "x-api-key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "conversation_001",
    "message": {
      "sender": "scammer",
      "text": "You won lottery! Call 9876543210",
      "timestamp": "2026-02-05T15:30:00Z",
      "message_id": "msg_conv_001"
    },
    "conversation_history": [],
    "metadata": {
      "channel": "SMS",
      "language": "en",
      "locale": "en-IN"
    }
  }'

# Second message (same session_id)
curl -X POST "http://localhost:8000/api/v1/process-message" \
  -H "x-api-key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "conversation_001",
    "message": {
      "sender": "scammer",
      "text": "Send money to account 1234567890 IFSC SBIN0001234",
      "timestamp": "2026-02-05T15:32:00Z",
      "message_id": "msg_conv_002"
    },
    "conversation_history": [
      {
        "sender": "scammer",
        "text": "You won lottery! Call 9876543210",
        "timestamp": "2026-02-05T15:30:00Z",
        "message_id": "msg_conv_001"
      }
    ],
    "metadata": {
      "channel": "SMS",
      "language": "en",
      "locale": "en-IN"
    }
  }'
```

---

### **3. Error Test Cases**

#### **Test Case 3.1: Missing API Key**
```bash
curl -X POST "http://localhost:8000/api/v1/process-message" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_error_001",
    "message": {
      "sender": "user",
      "text": "Test message",
      "timestamp": "2026-02-05T15:30:00Z",
      "message_id": "msg_error_001"
    },
    "conversation_history": [],
    "metadata": {
      "channel": "SMS",
      "language": "en",
      "locale": "en-IN"
    }
  }'
```

**Expected Response:**
```json
{
  "status": "error",
  "message": "Invalid or missing API key",
  "error_code": "AUTHENTICATION_ERROR"
}
```
**Status Code:** `401 Unauthorized`

#### **Test Case 3.2: Invalid API Key**
```bash
curl -X POST "http://localhost:8000/api/v1/process-message" \
  -H "x-api-key: invalid-key" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_error_002",
    "message": {
      "sender": "user",
      "text": "Test message",
      "timestamp": "2026-02-05T15:30:00Z",
      "message_id": "msg_error_002"
    },
    "conversation_history": [],
    "metadata": {
      "channel": "SMS",
      "language": "en",
      "locale": "en-IN"
    }
  }'
```

#### **Test Case 3.3: Missing Required Fields**
```bash
curl -X POST "http://localhost:8000/api/v1/process-message" \
  -H "x-api-key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_error_003"
  }'
```

**Expected Response:**
```json
{
  "status": "error",
  "message": "Request validation failed",
  "error_code": "VALIDATION_ERROR",
  "details": [
    {
      "type": "missing",
      "loc": ["message"],
      "msg": "Field required"
    }
  ]
}
```
**Status Code:** `400 Bad Request`

#### **Test Case 3.4: Empty Session ID**
```bash
curl -X POST "http://localhost:8000/api/v1/process-message" \
  -H "x-api-key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "",
    "message": {
      "sender": "user",
      "text": "Test message",
      "timestamp": "2026-02-05T15:30:00Z",
      "message_id": "msg_error_004"
    },
    "conversation_history": [],
    "metadata": {
      "channel": "SMS",
      "language": "en",
      "locale": "en-IN"
    }
  }'
```

#### **Test Case 3.5: Empty Message Text**
```bash
curl -X POST "http://localhost:8000/api/v1/process-message" \
  -H "x-api-key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_error_005",
    "message": {
      "sender": "user",
      "text": "",
      "timestamp": "2026-02-05T15:30:00Z",
      "message_id": "msg_error_005"
    },
    "conversation_history": [],
    "metadata": {
      "channel": "SMS",
      "language": "en",
      "locale": "en-IN"
    }
  }'
```

#### **Test Case 3.6: Invalid Session ID Format**
```bash
curl -X POST "http://localhost:8000/api/v1/process-message" \
  -H "x-api-key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "invalid@session#id!",
    "message": {
      "sender": "user",
      "text": "Test message",
      "timestamp": "2026-02-05T15:30:00Z",
      "message_id": "msg_error_006"
    },
    "conversation_history": [],
    "metadata": {
      "channel": "SMS",
      "language": "en",
      "locale": "en-IN"
    }
  }'
```

---

### **4. Ping Endpoint (Serverless)**

#### **GET /api/ping**

**Purpose:** Verify serverless function is working

```bash
curl -X GET "http://localhost:8000/api/ping"
```

**Expected Response:**
```json
{
  "status": "alive",
  "timestamp": 1738766400.123,
  "message": "Serverless function is working!"
}
```

---

## 🧪 PowerShell Test Script

Create `test_endpoints.ps1`:

```powershell
# Agentic Honeypot API Endpoint Tests

$baseUrl = "http://localhost:8000"
$apiKey = "test-key-123"
$headers = @{
    "x-api-key" = $apiKey
    "Content-Type" = "application/json"
}

Write-Host "🍯 AGENTIC HONEYPOT - ENDPOINT TESTS 🍯" -ForegroundColor Yellow
Write-Host "=" * 50

# Test 1: Health Check
Write-Host "`n🎯 TEST 1: Health Check" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "✅ Health Check: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Lottery Scam
Write-Host "`n🎯 TEST 2: Lottery Scam Detection" -ForegroundColor Cyan
$lotteryPayload = @{
    session_id = "test_lottery_ps"
    message = @{
        sender = "scammer"
        text = "You won 50000 rupees! Send 500 to 9876543210@paytm"
        timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        message_id = "msg_lottery_ps"
    }
    conversation_history = @()
    metadata = @{
        channel = "SMS"
        language = "en"
        locale = "en-IN"
    }
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/process-message" -Method Post -Headers $headers -Body $lotteryPayload
    Write-Host "✅ Scam Detected: $($response.scam_detected)" -ForegroundColor Green
    Write-Host "📊 Intelligence Score: $($response.engagement_metrics.intelligence_score)" -ForegroundColor Blue
} catch {
    Write-Host "❌ Lottery Test Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Clean Message
Write-Host "`n🎯 TEST 3: Clean Message" -ForegroundColor Cyan
$cleanPayload = @{
    session_id = "test_clean_ps"
    message = @{
        sender = "user"
        text = "Hello, how are you today?"
        timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        message_id = "msg_clean_ps"
    }
    conversation_history = @()
    metadata = @{
        channel = "SMS"
        language = "en"
        locale = "en-IN"
    }
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/process-message" -Method Post -Headers $headers -Body $cleanPayload
    Write-Host "✅ Scam Detected: $($response.scam_detected)" -ForegroundColor Green
    Write-Host "📊 Intelligence Score: $($response.engagement_metrics.intelligence_score)" -ForegroundColor Blue
} catch {
    Write-Host "❌ Clean Message Test Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Invalid API Key
Write-Host "`n🎯 TEST 4: Invalid API Key" -ForegroundColor Cyan
$invalidHeaders = @{
    "x-api-key" = "invalid-key"
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/process-message" -Method Post -Headers $invalidHeaders -Body $cleanPayload
    Write-Host "❌ Should have failed with invalid API key" -ForegroundColor Red
} catch {
    Write-Host "✅ Correctly rejected invalid API key" -ForegroundColor Green
}

Write-Host "`n✅ All endpoint tests completed!" -ForegroundColor Yellow
```

---

## 🚀 Quick Test Commands

**Start Server:**
```bash
cd agentic-honeypot-main
$env:PYTHONPATH='src'
python -m uvicorn honeypot.main:create_app --factory --reload --host 0.0.0.0 --port 8000
```

**Quick Health Check:**
```bash
curl http://localhost:8000/health
```

**Quick Scam Test:**
```bash
curl -X POST "http://localhost:8000/api/v1/process-message" \
  -H "x-api-key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"quick_test","message":{"sender":"scammer","text":"You won lottery! Send money!","timestamp":"2026-02-05T15:30:00Z","message_id":"quick"},"conversation_history":[],"metadata":{"channel":"SMS","language":"en","locale":"en-IN"}}'
```

---

## 📊 Expected Test Results

- ✅ **Health Check:** Returns healthy status
- ✅ **Scam Detection:** Identifies scam messages correctly
- ✅ **Intelligence Extraction:** Extracts phone numbers, UPI IDs, bank accounts
- ✅ **AI Responses:** Generates engaging responses for scams
- ✅ **Clean Messages:** Properly ignores non-scam content
- ✅ **Error Handling:** Returns appropriate error codes
- ✅ **Authentication:** Validates API keys correctly

---

*All endpoints tested and verified on February 5, 2026*