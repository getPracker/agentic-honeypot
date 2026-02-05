# 📮 Postman Testing Guide - Agentic Honeypot Deployed API

## 🌐 **Deployed URL Information**

Based on the GitHub repository `https://github.com/getPracker/agentic-honeypot`, the deployed API should be accessible at one of these potential URLs:

**Possible Deployment URLs:**
- `https://agentic-honeypot.vercel.app` (Vercel)
- `https://agentic-honeypot.onrender.com` (Render)
- `https://agentic-honeypot.railway.app` (Railway)
- Or a custom domain provided by the deployer

**⚠️ Note:** You'll need to get the actual deployed URL from the repository owner or deployment platform.

---

## 🚀 **Quick Setup in Postman**

### **Step 1: Create New Collection**
1. Open Postman
2. Click **"New"** → **"Collection"**
3. Name it: **"Agentic Honeypot API Tests"**
4. Add description: **"Testing deployed scam detection API"**

### **Step 2: Set Collection Variables**
In your collection, go to **Variables** tab and add:

| Variable | Initial Value | Current Value |
|----------|---------------|---------------|
| `base_url` | `https://your-deployed-url.com` | `https://your-deployed-url.com` |
| `api_key` | `test-key-123` | `test-key-123` |

---

## 📋 **Test Requests to Add**

### **1. Health Check**

**Request Name:** `Health Check`
**Method:** `GET`
**URL:** `{{base_url}}/health`
**Headers:** None required

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "agentic-honeypot"
}
```

---

### **2. Lottery Scam Detection**

**Request Name:** `Test Lottery Scam`
**Method:** `POST`
**URL:** `{{base_url}}/api/v1/process-message`

**Headers:**
```
x-api-key: {{api_key}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "session_id": "postman_lottery_001",
  "message": {
    "sender": "scammer",
    "text": "Congratulations! You won ₹50,000 in KBC lottery! Send ₹500 to 9876543210@paytm to claim your prize!",
    "timestamp": "2026-02-05T10:00:00Z",
    "message_id": "msg_lottery_001"
  },
  "conversation_history": [],
  "metadata": {
    "channel": "SMS",
    "language": "en",
    "locale": "en-IN",
    "source_ip": "192.168.1.100"
  }
}
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
    "phone_numbers": [
      {
        "number": "9876543210",
        "country_code": "+91",
        "confidence": 0.9
      }
    ],
    "upi_ids": ["9876543210@paytm"],
    "keywords": ["won", "lottery", "send", "money"]
  },
  "session_id": "postman_lottery_001"
}
```

---

### **3. Bank Fraud Detection**

**Request Name:** `Test Bank Fraud`
**Method:** `POST`
**URL:** `{{base_url}}/api/v1/process-message`

**Headers:**
```
x-api-key: {{api_key}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "session_id": "postman_bank_001",
  "message": {
    "sender": "scammer",
    "text": "URGENT! Your bank account will be blocked in 24 hours. Update KYC by calling 9876543210 immediately!",
    "timestamp": "2026-02-05T10:00:00Z",
    "message_id": "msg_bank_001"
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

### **4. Investment Scam with Bank Details**

**Request Name:** `Test Investment Scam`
**Method:** `POST`
**URL:** `{{base_url}}/api/v1/process-message`

**Headers:**
```
x-api-key: {{api_key}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "session_id": "postman_investment_001",
  "message": {
    "sender": "scammer",
    "text": "Invest ₹10,000 today and get ₹1,00,000 in 30 days! Guaranteed returns! Transfer to account 1234567890 IFSC SBIN0001234",
    "timestamp": "2026-02-05T10:00:00Z",
    "message_id": "msg_investment_001"
  },
  "conversation_history": [],
  "metadata": {
    "channel": "WhatsApp",
    "language": "en",
    "locale": "en-IN"
  }
}
```

---

### **5. UPI Fraud Detection**

**Request Name:** `Test UPI Fraud`
**Method:** `POST`
**URL:** `{{base_url}}/api/v1/process-message`

**Headers:**
```
x-api-key: {{api_key}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "session_id": "postman_upi_001",
  "message": {
    "sender": "scammer",
    "text": "Send ₹1000 to 9876543210@paytm for verification. You will get ₹10,000 cashback instantly!",
    "timestamp": "2026-02-05T10:00:00Z",
    "message_id": "msg_upi_001"
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

### **6. Clean Message (No Scam)**

**Request Name:** `Test Clean Message`
**Method:** `POST`
**URL:** `{{base_url}}/api/v1/process-message`

**Headers:**
```
x-api-key: {{api_key}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "session_id": "postman_clean_001",
  "message": {
    "sender": "user",
    "text": "Hello, how are you doing today? Hope you are having a great day!",
    "timestamp": "2026-02-05T10:00:00Z",
    "message_id": "msg_clean_001"
  },
  "conversation_history": [],
  "metadata": {
    "channel": "SMS",
    "language": "en",
    "locale": "en-IN"
  }
}
```

**Expected Response:**
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
    "phone_numbers": [],
    "upi_ids": [],
    "keywords": []
  },
  "session_id": "postman_clean_001"
}
```

---

### **7. Multi-turn Conversation**

**Request Name:** `Multi-turn Conversation - Turn 1`
**Method:** `POST`
**URL:** `{{base_url}}/api/v1/process-message`

**Headers:**
```
x-api-key: {{api_key}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "session_id": "postman_conversation_001",
  "message": {
    "sender": "scammer",
    "text": "You won lottery! Call 9876543210",
    "timestamp": "2026-02-05T10:00:00Z",
    "message_id": "msg_conv_001"
  },
  "conversation_history": [],
  "metadata": {
    "channel": "SMS",
    "language": "en",
    "locale": "en-IN"
  }
}
```

**Request Name:** `Multi-turn Conversation - Turn 2`
**Method:** `POST`
**URL:** `{{base_url}}/api/v1/process-message`

**Headers:**
```
x-api-key: {{api_key}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "session_id": "postman_conversation_001",
  "message": {
    "sender": "scammer",
    "text": "Send money to account 1234567890 IFSC SBIN0001234",
    "timestamp": "2026-02-05T10:02:00Z",
    "message_id": "msg_conv_002"
  },
  "conversation_history": [
    {
      "sender": "scammer",
      "text": "You won lottery! Call 9876543210",
      "timestamp": "2026-02-05T10:00:00Z",
      "message_id": "msg_conv_001"
    }
  ],
  "metadata": {
    "channel": "SMS",
    "language": "en",
    "locale": "en-IN"
  }
}
```

---

## ❌ **Error Testing**

### **8. Missing API Key**

**Request Name:** `Error - Missing API Key`
**Method:** `POST`
**URL:** `{{base_url}}/api/v1/process-message`

**Headers:**
```
Content-Type: application/json
```
*(No x-api-key header)*

**Body (raw JSON):**
```json
{
  "session_id": "postman_error_001",
  "message": {
    "sender": "user",
    "text": "Test message",
    "timestamp": "2026-02-05T10:00:00Z",
    "message_id": "msg_error_001"
  },
  "conversation_history": [],
  "metadata": {
    "channel": "SMS",
    "language": "en",
    "locale": "en-IN"
  }
}
```

**Expected Response:**
```json
{
  "status": "error",
  "message": "Invalid or missing API key",
  "error_code": "AUTHENTICATION_ERROR"
}
```
**Expected Status Code:** `401 Unauthorized`

---

### **9. Invalid API Key**

**Request Name:** `Error - Invalid API Key`
**Method:** `POST`
**URL:** `{{base_url}}/api/v1/process-message`

**Headers:**
```
x-api-key: invalid-key-123
Content-Type: application/json
```

**Body:** *(Same as above)*

**Expected Status Code:** `401 Unauthorized`

---

### **10. Missing Required Fields**

**Request Name:** `Error - Missing Fields`
**Method:** `POST`
**URL:** `{{base_url}}/api/v1/process-message`

**Headers:**
```
x-api-key: {{api_key}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "session_id": "postman_error_003"
}
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
**Expected Status Code:** `400 Bad Request`

---

## 🧪 **Postman Tests (Automated Validation)**

Add these **Tests** to your requests for automated validation:

### **For Successful Scam Detection:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has required fields", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('status');
    pm.expect(jsonData).to.have.property('scam_detected');
    pm.expect(jsonData).to.have.property('session_id');
});

pm.test("Scam is detected", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.scam_detected).to.be.true;
});

pm.test("AI response is generated", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.agent_response).to.not.be.null;
    pm.expect(jsonData.agent_response.length).to.be.above(10);
});

pm.test("Intelligence is extracted", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.extracted_intelligence).to.be.an('object');
});

pm.test("Response time is acceptable", function () {
    pm.expect(pm.response.responseTime).to.be.below(5000);
});
```

### **For Clean Messages:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("No scam detected", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.scam_detected).to.be.false;
});

pm.test("No AI response for clean message", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.agent_response).to.be.null;
});
```

### **For Error Cases:**
```javascript
pm.test("Status code is 401", function () {
    pm.response.to.have.status(401);
});

pm.test("Error message is present", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('message');
    pm.expect(jsonData).to.have.property('error_code');
});
```

---

## 🎯 **Pre-built Collection JSON**

Save this as `Agentic_Honeypot_Tests.postman_collection.json`:

```json
{
  "info": {
    "name": "Agentic Honeypot API Tests",
    "description": "Comprehensive testing suite for the deployed Agentic Honeypot API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "https://your-deployed-url.com",
      "type": "string"
    },
    {
      "key": "api_key",
      "value": "test-key-123",
      "type": "string"
    }
  ],
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/health",
          "host": ["{{base_url}}"],
          "path": ["health"]
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test('Status code is 200', function () {",
              "    pm.response.to.have.status(200);",
              "});",
              "",
              "pm.test('Service is healthy', function () {",
              "    const jsonData = pm.response.json();",
              "    pm.expect(jsonData.status).to.eql('healthy');",
              "    pm.expect(jsonData.service).to.eql('agentic-honeypot');",
              "});"
            ]
          }
        }
      ]
    },
    {
      "name": "Test Lottery Scam",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "x-api-key",
            "value": "{{api_key}}"
          },
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"session_id\": \"postman_lottery_001\",\n  \"message\": {\n    \"sender\": \"scammer\",\n    \"text\": \"Congratulations! You won ₹50,000 in KBC lottery! Send ₹500 to 9876543210@paytm to claim your prize!\",\n    \"timestamp\": \"2026-02-05T10:00:00Z\",\n    \"message_id\": \"msg_lottery_001\"\n  },\n  \"conversation_history\": [],\n  \"metadata\": {\n    \"channel\": \"SMS\",\n    \"language\": \"en\",\n    \"locale\": \"en-IN\",\n    \"source_ip\": \"192.168.1.100\"\n  }\n}"
        },
        "url": {
          "raw": "{{base_url}}/api/v1/process-message",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "process-message"]
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test('Status code is 200', function () {",
              "    pm.response.to.have.status(200);",
              "});",
              "",
              "pm.test('Scam is detected', function () {",
              "    const jsonData = pm.response.json();",
              "    pm.expect(jsonData.scam_detected).to.be.true;",
              "});",
              "",
              "pm.test('AI response is generated', function () {",
              "    const jsonData = pm.response.json();",
              "    pm.expect(jsonData.agent_response).to.not.be.null;",
              "});",
              "",
              "pm.test('Phone number extracted', function () {",
              "    const jsonData = pm.response.json();",
              "    pm.expect(jsonData.extracted_intelligence.phone_numbers).to.be.an('array');",
              "    pm.expect(jsonData.extracted_intelligence.phone_numbers.length).to.be.above(0);",
              "});"
            ]
          }
        }
      ]
    }
  ]
}
```

---

## 🚀 **How to Import and Run**

### **Method 1: Import Collection**
1. Download the JSON file above
2. In Postman, click **Import**
3. Select the JSON file
4. Update the `base_url` variable with your deployed URL

### **Method 2: Manual Setup**
1. Create new collection
2. Add each request manually using the details above
3. Set up collection variables
4. Add test scripts for validation

### **Method 3: Run Collection**
1. Click **Runner** in Postman
2. Select your collection
3. Click **Run Agentic Honeypot API Tests**
4. View results and performance metrics

---

## 📊 **What to Look For**

### **✅ Success Indicators:**
- Status code 200 for valid requests
- `scam_detected: true` for scam messages
- AI responses generated for scams
- Intelligence extracted (phone numbers, UPI IDs)
- Response time under 5 seconds

### **❌ Failure Indicators:**
- 500 Internal Server Error (deployment issues)
- 401 Unauthorized (API key problems)
- No AI responses (API quota exceeded)
- Timeout errors (server overload)

### **🔍 Key Metrics to Monitor:**
- **Response Time**: Should be < 5 seconds
- **Success Rate**: Should be 100% for valid requests
- **AI Response Quality**: Engaging and contextual
- **Intelligence Accuracy**: Correct extraction of phone/UPI

---

## 🛠️ **Troubleshooting**

### **Common Issues:**

1. **"Connection refused"**
   - Check if the deployed URL is correct
   - Verify the service is running

2. **"Invalid API key"**
   - Check the API key in collection variables
   - Verify the deployed service has the same API key

3. **"Timeout"**
   - Increase timeout in Postman settings
   - Check if the AI service is responding

4. **"No AI response"**
   - API quota might be exceeded
   - Check server logs for errors

---

## 📱 **Mobile Testing**

You can also test from mobile:
1. Install Postman mobile app
2. Import the collection
3. Run tests on mobile network
4. Test different network conditions

---

**🎯 Ready to test! Update the `base_url` with your actual deployed URL and start testing the Agentic Honeypot API!**