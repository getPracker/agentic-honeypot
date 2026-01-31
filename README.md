# 🍯 Agentic Honeypot - AI-Powered Scam Detection System

An intelligent honeypot system that uses AI agents to detect, engage, and extract intelligence from scammers.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Features

### Core Capabilities
- ✅ **Real-time Scam Detection** - Multi-type classification (lottery, bank fraud, phishing, etc.)
- ✅ **AI-Powered Engagement** - Realistic personas that keep scammers engaged
- ✅ **Intelligence Extraction** - Automatically extracts phone numbers, bank accounts, UPI IDs
- ✅ **External Integration** - Reports findings to external systems via callbacks
- ✅ **Enterprise Security** - Encryption, input sanitization, security headers
- ✅ **Comprehensive Testing** - 85+ tests with property-based testing

### AI Agent Personas
1. **Elderly Victim** - Trusting, tech-illiterate, polite
2. **Naive Student** - Eager, broke, optimistic  
3. **Curious Skeptic** - Cautious, asks questions

### Scam Types Detected
- 💰 Lottery/Prize scams
- 🏦 Bank fraud
- 📱 UPI/Payment scams
- 🎣 Phishing attacks
- 💼 Investment scams
- 🛠️ Tech support scams

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/getPracker/agentic-honeypot.git
cd agentic-honeypot

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run with Docker Compose
docker-compose up -d

# Verify
curl http://localhost:8000/health
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set Python path
export PYTHONPATH=src  # Linux/Mac
$env:PYTHONPATH='src'  # Windows

# Run server
python -m uvicorn honeypot.main:create_app --factory --reload

# Access API
open http://localhost:8000/docs
```

## 📖 Documentation

- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment options
- **[Testing Guide](TESTING_GUIDE.md)** - How to test the system
- **[Public Deployment](PUBLIC_DEPLOYMENT.md)** - Deploy for hackathon demos
- **[Verification Report](VERIFICATION_REPORT.md)** - System validation results

## 🔧 Configuration

### Required Environment Variables

```env
# Encryption
ENCRYPTION_KEY=your_fernet_key_here

# Authentication
API_KEYS=["your-api-key"]

# AI Provider
GEMINI_API_KEY=your_gemini_api_key

# Callback
GUVI_CALLBACK_URL=https://hackathon.guvi.in/api/updateHoneyPotFinalResult
```

### Generate Keys

```bash
# Encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# API key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📡 API Usage

### Process a Message

```bash
curl -X POST http://localhost:8000/api/v1/process-message \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -d '{
    "session_id": "test_session",
    "message": {
      "sender": "scammer",
      "text": "You won ₹50,000! Send ₹500 to claim!",
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

### Response

```json
{
  "status": "success",
  "scam_detected": true,
  "agent_response": "Wow! I won money? That's amazing! But why do I need to send ₹500 first?",
  "extracted_intelligence": {
    "phone_numbers": [],
    "upi_ids": [],
    "keywords": ["won", "lottery", "send", "money"]
  },
  "engagement_metrics": {
    "message_count": 2,
    "intelligence_score": 0.6
  }
}
```

## 🧪 Testing

### Run All Tests

```bash
$env:PYTHONPATH='src'
python -m pytest tests -v
```

### Run Specific Tests

```bash
# Scam detection
python -m pytest tests/test_scam_detector.py -v

# AI agent
python -m pytest tests/test_ai_agent.py -v

# Security
python -m pytest tests/test_security.py -v
```

### Quick Test Script

```bash
python quick_test.py
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         API Gateway (FastAPI)           │
│  - Authentication                       │
│  - Request Validation                   │
│  - Security Headers                     │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│      MessageProcessor (Orchestrator)    │
└──────────────┬──────────────────────────┘
               ↓
    ┌──────────┴──────────┐
    ↓                     ↓
┌─────────────┐    ┌──────────────┐
│SessionMgr   │    │ScamDetector  │
│(State)      │    │(Classification)
└─────────────┘    └──────────────┘
    ↓                     ↓
┌─────────────┐    ┌──────────────┐
│AIAgent      │    │IntelExtractor│
│(Gemini/GPT) │    │(Data Mining) │
└─────────────┘    └──────────────┘
    ↓                     ↓
┌─────────────────────────────────┐
│      CallbackHandler            │
│      → External Systems         │
└─────────────────────────────────┘
```

## 🔒 Security Features

- ✅ **Fernet Encryption** - Symmetric encryption for sensitive data
- ✅ **Input Sanitization** - Prevents injection attacks
- ✅ **Log Sanitization** - Redacts sensitive information
- ✅ **Security Headers** - HSTS, CSP, X-Frame-Options, etc.
- ✅ **CORS Configuration** - Controlled cross-origin access
- ✅ **API Key Authentication** - Secure endpoint access

## 📊 System Requirements

- **Python**: 3.11 or higher
- **Memory**: 512MB minimum, 1GB recommended
- **Storage**: 100MB for application, more for logs/data
- **Network**: Internet access for AI API calls

## 🤝 Contributing

This is a hackathon project. For issues or suggestions:
1. Open an issue on GitHub
2. Submit a pull request
3. Contact the maintainers

## 📄 License

MIT License - see LICENSE file for details

## 🏆 Hackathon Information

**Event**: GUVI Hackathon 2026
**Category**: AI/ML Security
**Team**: [Your Team Name]

## 🙏 Acknowledgments

- Google Gemini for AI capabilities
- FastAPI for the excellent web framework
- Hypothesis for property-based testing
- GUVI for hosting the hackathon

## 📞 Support

- **Documentation**: See `/docs` directory
- **API Docs**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **Email**: [your-email]

---

**Built with ❤️ for safer digital communications**

🍯 **Catch scammers, protect users, extract intelligence!**