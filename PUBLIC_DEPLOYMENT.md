# Public Deployment & Testing Guide

## 🌐 How to Deploy Publicly for Hackathon

### Option 1: ngrok (Fastest - Recommended for Demo) ⚡

**ngrok** creates a public URL tunnel to your local server - perfect for hackathon demos!

#### Step 1: Install ngrok
```powershell
# Download from https://ngrok.com/download
# Or use chocolatey:
choco install ngrok

# Or download directly and extract
```

#### Step 2: Start Your Server
```powershell
cd c:\Users\Sahil\Downloads\agentic-honeypot-main\agentic-honeypot-main
$env:PYTHONPATH='src'
python -m uvicorn honeypot.main:create_app --factory --host 0.0.0.0 --port 8000
```

#### Step 3: Create Public Tunnel
**Open a NEW terminal**:
```powershell
ngrok http 8000
```

**You'll get output like**:
```
Session Status                online
Account                       your-email@example.com
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
```

#### Step 4: Test Publicly
Your API is now accessible at: `https://abc123.ngrok.io`

**Test from anywhere**:
```bash
curl -X POST https://abc123.ngrok.io/api/v1/process-message \
  -H "Content-Type: application/json" \
  -H "x-api-key: test-key-123" \
  -d '{
    "session_id": "public_test_001",
    "message": {
      "sender": "scammer",
      "text": "You won lottery! Send money!",
      "timestamp": "2026-01-28T10:00:00Z",
      "message_id": "msg_001"
    },
    "conversation_history": [],
    "metadata": {
      "channel": "SMS",
      "language": "en",
      "locale": "en-IN"
    }
  }'
```

**Share this URL** with hackathon judges: `https://abc123.ngrok.io/docs`

---

### Option 2: Railway.app (Free Hosting) 🚂

#### Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"

#### Step 2: Prepare for Deployment

Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn honeypot.main:create_app --factory --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Create `Procfile`:
```
web: uvicorn honeypot.main:create_app --factory --host 0.0.0.0 --port $PORT
```

Create `runtime.txt`:
```
python-3.11
```

Update `requirements.txt` (if not exists):
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
cryptography==41.0.7
openai==1.3.7
google-generativeai==0.3.1
httpx==0.25.2
tenacity==8.2.3
```

#### Step 3: Deploy
1. Push code to GitHub
2. Connect Railway to your repo
3. Add environment variables in Railway dashboard:
   - `ENCRYPTION_KEY`
   - `GEMINI_API_KEY`
   - `API_KEYS`
   - `GUVI_CALLBACK_URL`

#### Step 4: Get Public URL
Railway will provide: `https://your-app.railway.app`

---

### Option 3: Render.com (Free Tier) 🎨

#### Step 1: Create Account
1. Go to https://render.com
2. Sign up with GitHub

#### Step 2: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repo
3. Configure:
   - **Name**: agentic-honeypot
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn honeypot.main:create_app --factory --host 0.0.0.0 --port $PORT`

#### Step 3: Add Environment Variables
In Render dashboard, add:
```
ENCRYPTION_KEY=DGRP2s9PsfDib7V9rKaa4Dld-DfTaqPiCkIJ3Y1EOWQ=
GEMINI_API_KEY=your_key_here
API_KEYS=["test-key-123"]
GUVI_CALLBACK_URL=https://hackathon.guvi.in/api/updateHoneyPotFinalResult
DATABASE_URL=sqlite:///honeypot.db
```

#### Step 4: Deploy
Render will build and deploy automatically.
URL: `https://agentic-honeypot.onrender.com`

---

### Option 4: Docker + Cloud Run (Production-Ready) 🐳

#### Step 1: Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY .env .env

# Set Python path
ENV PYTHONPATH=/app/src

# Expose port
EXPOSE 8080

# Run application
CMD ["uvicorn", "honeypot.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8080"]
```

#### Step 2: Build and Test Locally
```powershell
docker build -t agentic-honeypot .
docker run -p 8080:8080 --env-file .env agentic-honeypot
```

#### Step 3: Deploy to Google Cloud Run
```bash
# Install gcloud CLI
# Then:
gcloud auth login
gcloud config set project your-project-id

# Build and push
gcloud builds submit --tag gcr.io/your-project-id/agentic-honeypot

# Deploy
gcloud run deploy agentic-honeypot \
  --image gcr.io/your-project-id/agentic-honeypot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 🎯 Public Testing Scenarios

### Scenario 1: Share Interactive Demo

**Create a simple HTML page** (`public_demo.html`):

```html
<!DOCTYPE html>
<html>
<head>
    <title>Agentic Honeypot Demo</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
        input, textarea { width: 100%; padding: 10px; margin: 10px 0; }
        button { background: #4CAF50; color: white; padding: 15px 32px; border: none; cursor: pointer; }
        .response { background: white; padding: 15px; margin-top: 20px; border-radius: 5px; }
        .scam { color: red; font-weight: bold; }
        .safe { color: green; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🍯 Agentic Honeypot - Live Demo</h1>
        <p>Test the AI-powered scam detection system!</p>
        
        <label>Enter a message to test:</label>
        <textarea id="message" rows="4" placeholder="Example: You won ₹50,000! Send money to claim..."></textarea>
        
        <button onclick="testMessage()">🔍 Analyze Message</button>
        
        <div id="result" class="response" style="display:none;">
            <h3>Results:</h3>
            <div id="resultContent"></div>
        </div>
    </div>

    <script>
        const API_URL = 'https://YOUR-NGROK-URL.ngrok.io/api/v1/process-message';
        const API_KEY = 'test-key-123';

        async function testMessage() {
            const message = document.getElementById('message').value;
            if (!message) {
                alert('Please enter a message');
                return;
            }

            const payload = {
                session_id: 'demo_' + Date.now(),
                message: {
                    sender: 'user',
                    text: message,
                    timestamp: new Date().toISOString(),
                    message_id: 'msg_' + Date.now()
                },
                conversation_history: [],
                metadata: {
                    channel: 'WEB',
                    language: 'en',
                    locale: 'en-IN'
                }
            };

            try {
                const response = await fetch(API_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'x-api-key': API_KEY
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();
                displayResult(data);
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }

        function displayResult(data) {
            const resultDiv = document.getElementById('result');
            const contentDiv = document.getElementById('resultContent');
            
            let html = '';
            
            if (data.scam_detected) {
                html += '<p class="scam">⚠️ SCAM DETECTED!</p>';
                html += `<p><strong>Confidence:</strong> ${(data.confidence || 0.9) * 100}%</p>`;
                
                if (data.agent_response) {
                    html += `<p><strong>🤖 AI Response:</strong><br>${data.agent_response}</p>`;
                }
                
                const intel = data.extracted_intelligence;
                if (intel) {
                    html += '<p><strong>🔍 Extracted Intelligence:</strong></p><ul>';
                    if (intel.phone_numbers?.length) {
                        html += `<li>📞 Phone: ${intel.phone_numbers.map(p => p.number).join(', ')}</li>`;
                    }
                    if (intel.upi_ids?.length) {
                        html += `<li>💳 UPI: ${intel.upi_ids.join(', ')}</li>`;
                    }
                    if (intel.keywords?.length) {
                        html += `<li>🔑 Keywords: ${intel.keywords.slice(0, 5).join(', ')}</li>`;
                    }
                    html += '</ul>';
                }
            } else {
                html += '<p class="safe">✅ No scam detected</p>';
                html += '<p>This message appears to be legitimate.</p>';
            }
            
            contentDiv.innerHTML = html;
            resultDiv.style.display = 'block';
        }
    </script>
</body>
</html>
```

**Host this on**:
- GitHub Pages
- Netlify
- Vercel

---

### Scenario 2: Postman Collection for Judges

Create `Honeypot_API.postman_collection.json`:

```json
{
  "info": {
    "name": "Agentic Honeypot API",
    "description": "Test collection for hackathon judges"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/health"
      }
    },
    {
      "name": "Test Lottery Scam",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/api/v1/process-message",
        "header": [
          {"key": "x-api-key", "value": "{{api_key}}"},
          {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"session_id\": \"judge_test_lottery\",\n  \"message\": {\n    \"sender\": \"scammer\",\n    \"text\": \"Congratulations! You won ₹50,000 in KBC lottery! Send ₹500 to 9876543210@paytm\",\n    \"timestamp\": \"2026-01-28T10:00:00Z\",\n    \"message_id\": \"msg_001\"\n  },\n  \"conversation_history\": [],\n  \"metadata\": {\n    \"channel\": \"SMS\",\n    \"language\": \"en\",\n    \"locale\": \"en-IN\"\n  }\n}"
        }
      }
    }
  ],
  "variable": [
    {"key": "base_url", "value": "https://your-url.ngrok.io"},
    {"key": "api_key", "value": "test-key-123"}
  ]
}
```

Share this collection link with judges!

---

### Scenario 3: Live Demo Dashboard

Create a real-time monitoring dashboard showing:
- 📊 Total messages processed
- 🚨 Scams detected
- 🔍 Intelligence extracted
- 📈 Live statistics

Use **Streamlit** for quick dashboard:

```python
# dashboard.py
import streamlit as st
import requests
import json

st.title("🍯 Agentic Honeypot - Live Dashboard")

API_URL = st.text_input("API URL", "http://localhost:8000")
API_KEY = st.text_input("API Key", "test-key-123", type="password")

message = st.text_area("Test Message", "You won lottery! Send money!")

if st.button("🔍 Analyze"):
    payload = {
        "session_id": f"dashboard_{int(time.time())}",
        "message": {
            "sender": "user",
            "text": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message_id": f"msg_{int(time.time())}"
        },
        "conversation_history": [],
        "metadata": {"channel": "WEB", "language": "en", "locale": "en-IN"}
    }
    
    response = requests.post(
        f"{API_URL}/api/v1/process-message",
        json=payload,
        headers={"x-api-key": API_KEY}
    )
    
    data = response.json()
    
    if data['scam_detected']:
        st.error("⚠️ SCAM DETECTED!")
        st.write("**AI Response:**", data.get('agent_response'))
        st.json(data['extracted_intelligence'])
    else:
        st.success("✅ No scam detected")
```

Run: `streamlit run dashboard.py`

---

## 📱 Mobile Testing

### Test from Phone Browser
1. Deploy with ngrok
2. Open ngrok URL on phone: `https://abc123.ngrok.io/docs`
3. Use Swagger UI to test

### WhatsApp Integration (Advanced)
Use **Twilio** to connect WhatsApp → Your API

---

## 🎬 Demo Presentation Tips

### 1. Prepare Test Cases
```
✅ Lottery Scam: "You won ₹50,000! Send ₹500"
✅ Bank Fraud: "Account blocked! Call 9876543210"
✅ Investment: "Invest ₹10,000, get ₹1,00,000"
✅ Clean Message: "Hello, how are you?"
```

### 2. Show Live Metrics
- Response time
- Detection accuracy
- Intelligence extracted
- AI engagement quality

### 3. Demonstrate Multi-turn Conversation
Show how AI keeps scammer engaged across multiple messages

### 4. Show Callback Integration
Display GUVI endpoint receiving data in real-time

---

## 🔒 Security for Public Deployment

### Update `.env` for Production:
```env
# Use strong API keys
API_KEYS=["prod-key-$(openssl rand -hex 32)"]

# Rate limiting
RATE_LIMIT_PER_MINUTE=60

# CORS (if needed)
ALLOWED_ORIGINS=["https://your-frontend.com"]
```

### Add Rate Limiting:
```python
# In main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/process-message")
@limiter.limit("10/minute")
async def process_message(...):
    ...
```

---

## 📊 Monitoring Public Deployment

### Use ngrok's Web Interface
```
http://127.0.0.1:4040
```
Shows all requests in real-time!

### Log All Requests
Check server logs for:
- Request patterns
- Error rates
- Response times

---

## ✅ Pre-Demo Checklist

- [ ] Server running and accessible
- [ ] ngrok tunnel active
- [ ] Gemini API key working
- [ ] Test all scam scenarios
- [ ] Callback to GUVI working
- [ ] Swagger docs accessible
- [ ] Demo HTML page ready
- [ ] Postman collection prepared
- [ ] Backup plan if internet fails

---

**Recommended for Hackathon: Use ngrok + Swagger UI for live demo! 🎯**
