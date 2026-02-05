# 📮 Postman Setup for Your Vercel Deployment

## 🌐 **Your Deployed API**
**URL:** `https://agentic-honeypot-chi.vercel.app/`
**Status:** ✅ **LIVE AND WORKING**

---

## 🚀 **Quick Postman Setup**

### **Step 1: Create Collection**
1. Open Postman
2. Click **"New"** → **"Collection"**
3. Name: **"Agentic Honeypot - Vercel"**

### **Step 2: Set Collection Variables**
Go to **Variables** tab and add:

| Variable | Initial Value | Current Value |
|----------|---------------|---------------|
| `base_url` | `https://agentic-honeypot-chi.vercel.app` | `https://agentic-honeypot-chi.vercel.app` |
| `api_key` | `test-key-123` | `test-key-123` |

---

## 📋 **Essential Test Requests**

### **1. Health Check ✅**

**Request Name:** `Health Check`
**Method:** `GET`
**URL:** `{{base_url}}/health`
**Headers:** None required

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "agentic-honeypot",
  "timestamp": 1770280525.5530744,
  "mode": "stateless"
}
```

---

### **2. Lottery Scam Detection 🎯**

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
    "locale": "en-IN"
  }
}
```

---

### **3. Bank Fraud Detection 🏦**

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
    "text": "URGENT! Your bank account will be blocked in 24 hours. Call 9876543210 immediately to update KYC!",
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

### **4. UPI Fraud Detection 💳**

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
    "text": "Send ₹1000 to 9876543210@paytm for verification. Get ₹10,000 cashback instantly!",
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

### **5. Clean Message Test 🧹**

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
  "extracted_intelligence": {
    "phone_numbers": [],
    "upi_ids": [],
    "keywords": []
  }
}
```

---

## ❌ **Error Testing**

### **6. Missing API Key**

**Request Name:** `Error - Missing API Key`
**Method:** `POST`
**URL:** `{{base_url}}/api/v1/process-message`

**Headers:**
```
Content-Type: application/json
```
*(No x-api-key header)*

**Body:** *(Any valid JSON)*

**Expected Response:**
```json
{
  "status": "error",
  "message": "Invalid or missing API key",
  "error_code": "AUTHENTICATION_ERROR"
}
```
**Expected Status:** `401 Unauthorized`

---

### **7. Invalid API Key**

**Request Name:** `Error - Invalid API Key`
**Method:** `POST`
**URL:** `{{base_url}}/api/v1/process-message`

**Headers:**
```
x-api-key: invalid-key-123
Content-Type: application/json
```

**Expected Status:** `401 Unauthorized`

---

## 🧪 **Postman Tests (Add to each request)**

### **For Successful Requests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has required fields", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('status');
    pm.expect(jsonData).to.have.property('scam_detected');
});

pm.test("Response time is acceptable", function () {
    pm.expect(pm.response.responseTime).to.be.below(10000); // 10 seconds for serverless
});
```

### **For Scam Detection:**
```javascript
pm.test("Scam is detected", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.scam_detected).to.be.true;
});

pm.test("Intelligence extracted", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.extracted_intelligence).to.be.an('object');
});
```

### **For Error Cases:**
```javascript
pm.test("Status code is 401", function () {
    pm.response.to.have.status(401);
});

pm.test("Error response format", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('status', 'error');
    pm.expect(jsonData).to.have.property('error_code');
});
```

---

## 📱 **Ready-to-Import Collection**

Save this as `Vercel_Honeypot_Collection.json`:

```json
{
  "info": {
    "name": "Agentic Honeypot - Vercel Deployment",
    "description": "Testing the deployed Agentic Honeypot API on Vercel",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "https://agentic-honeypot-chi.vercel.app",
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
          "raw": "{\n  \"session_id\": \"postman_lottery_001\",\n  \"message\": {\n    \"sender\": \"scammer\",\n    \"text\": \"Congratulations! You won ₹50,000 in KBC lottery! Send ₹500 to 9876543210@paytm to claim your prize!\",\n    \"timestamp\": \"2026-02-05T10:00:00Z\",\n    \"message_id\": \"msg_lottery_001\"\n  },\n  \"conversation_history\": [],\n  \"metadata\": {\n    \"channel\": \"SMS\",\n    \"language\": \"en\",\n    \"locale\": \"en-IN\"\n  }\n}"
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
              "pm.test('Response has required fields', function () {",
              "    const jsonData = pm.response.json();",
              "    pm.expect(jsonData).to.have.property('status');",
              "    pm.expect(jsonData).to.have.property('scam_detected');",
              "});",
              "",
              "pm.test('Response time acceptable for serverless', function () {",
              "    pm.expect(pm.response.responseTime).to.be.below(10000);",
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

## 🎯 **Quick Test Steps**

### **Method 1: Manual Testing**
1. Create new collection in Postman
2. Set variables: `base_url` and `api_key`
3. Add the requests above
4. Run each test individually

### **Method 2: Import Collection**
1. Save the JSON above as a file
2. In Postman: **Import** → Select file
3. Run the entire collection

### **Method 3: Collection Runner**
1. Select your collection
2. Click **Runner**
3. Click **Run Collection**
4. View automated test results

---

## 🔍 **What to Expect**

### **✅ Success Indicators:**
- Health check returns status 200
- API requests return status 200
- `scam_detected` field present in responses
- Response times under 10 seconds (serverless cold start)

### **⚠️ Serverless Notes:**
- **First request** may be slow (cold start)
- **Subsequent requests** will be faster
- **Timeout** after 10 seconds is normal for Vercel

### **🚨 If Something Fails:**
- Check Vercel function logs
- Verify API key is correct
- Ensure JSON body is properly formatted
- Try again (serverless functions need warm-up)

---

## 🎉 **Your API is Ready!**

**Base URL:** `https://agentic-honeypot-chi.vercel.app`
**API Key:** `test-key-123`
**Status:** ✅ **LIVE AND WORKING**

**🚀 Start testing with Postman now!**

---

## 📊 **Live Demo URLs**

You can also test directly in browser:
- **Health Check:** https://agentic-honeypot-chi.vercel.app/health
- **API Docs:** https://agentic-honeypot-chi.vercel.app/docs (if available)
- **Interactive Testing:** Use Postman with the setup above

**Happy Testing! 🎯**