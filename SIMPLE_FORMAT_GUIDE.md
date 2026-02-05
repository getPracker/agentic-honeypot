# 🎯 Simple Response Format Guide

## ✅ **What You Wanted:**

You wanted the API to return a **simple format** like:
```json
{
    "status": "success",
    "reply": "Why is my account being suspended?"
}
```

Instead of the complex full response with all the engagement metrics.

## 🔧 **Solution: Query Parameter**

I've added a `format` query parameter to control the response format:

### **🌟 Simple Format (What You Want):**
**URL:** `http://localhost:8000/api/v1/process-message?format=simple`

**Response:**
```json
{
    "status": "success",
    "reply": "Why is my account being suspended?"
}
```

### **📊 Full Format (Original):**
**URL:** `http://localhost:8000/api/v1/process-message?format=full` (or default)

**Response:**
```json
{
    "status": "success",
    "scam_detected": false,
    "agent_response": "Why is my account being suspended?",
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
        "keywords": ["bank", "immediately", "account", "blocked"]
    },
    "session_id": "1fc994e9-f4c5-47ee-8806-90aeb969928f"
}
```

## 🎯 **Postman Setup for Simple Format:**

### **Method:** `POST`
### **URL:** `http://localhost:8000/api/v1/process-message?format=simple`
### **Headers:**
```
x-api-key: test-key-123
Content-Type: application/json
```

### **Body (camelCase - your preferred):**
```json
{
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
```

### **Expected Response:**
```json
{
    "status": "success",
    "reply": "Why is my account being suspended?"
}
```

## 🔄 **Response Logic:**

| Scenario | Simple Format Response |
|----------|----------------------|
| **Scam Detected + AI Response** | `{"status": "success", "reply": "AI response text"}` |
| **Scam Detected + No AI Response** | `{"status": "success", "reply": null}` |
| **Clean Message** | `{"status": "success", "reply": null}` |
| **Error** | Standard error response |

## 🎯 **Quick Test Commands:**

### **Simple Format:**
```bash
curl -X POST "http://localhost:8000/api/v1/process-message?format=simple" \
  -H "x-api-key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-session",
    "message": {
      "sender": "scammer",
      "text": "You won lottery! Send money!",
      "timestamp": 1769776085000
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

### **Full Format (Default):**
```bash
curl -X POST "http://localhost:8000/api/v1/process-message" \
  -H "x-api-key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{...same body...}'
```

## 🌐 **Comparison with Vercel:**

| Feature | Localhost Simple | Vercel | Localhost Full |
|---------|------------------|--------|----------------|
| **Format** | `{"status": "success", "reply": "..."}` | `{"status": "success", "reply": "..."}` | Full detailed response |
| **Speed** | ~3-6 seconds | ~1-2 seconds | ~3-6 seconds |
| **AI Response** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Intelligence Data** | ❌ Hidden | ❌ Not available | ✅ Full details |
| **Use Case** | **Perfect for your needs** | Public demos | Development/debugging |

## 🎉 **Perfect Solution:**

**Your localhost now provides the EXACT same simple format as Vercel!**

Just add `?format=simple` to your Postman URL and you'll get:
```json
{
    "status": "success",
    "reply": "Why is my account being suspended?"
}
```

**This is exactly what you wanted!** 🚀