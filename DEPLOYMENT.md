# Deployment Guide - Agentic Honeypot

## Quick Deployment Options

### Option 1: Docker (Recommended) 🐳

#### Prerequisites
- Docker installed
- Docker Compose installed

#### Steps

1. **Clone the repository**
```bash
git clone https://github.com/getPracker/agentic-honeypot.git
cd agentic-honeypot
```

2. **Create `.env` file**
```bash
cp .env.example .env
```

3. **Edit `.env` with your credentials**
```env
# Required
ENCRYPTION_KEY=DGRP2s9PsfDib7V9rKaa4Dld-DfTaqPiCkIJ3Y1EOWQ=
API_KEYS=["your-api-key-here"]
GEMINI_API_KEY=your_gemini_api_key_here
GUVI_CALLBACK_URL=https://hackathon.guvi.in/api/updateHoneyPotFinalResult

# Optional
OPENAI_API_KEY=your_openai_key_here
DEFAULT_LLM_PROVIDER=gemini
LOG_LEVEL=INFO
```

4. **Build and run**
```bash
docker-compose up -d
```

5. **Verify deployment**
```bash
curl http://localhost:8000/health
```

6. **View logs**
```bash
docker-compose logs -f
```

7. **Stop the service**
```bash
docker-compose down
```

---

### Option 2: Local Development 💻

#### Prerequisites
- Python 3.11+
- pip

#### Steps

1. **Clone and setup**
```bash
git clone https://github.com/getPracker/agentic-honeypot.git
cd agentic-honeypot
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Run the server**
```bash
# Windows
$env:PYTHONPATH='src'
python -m uvicorn honeypot.main:create_app --factory --reload

# Linux/Mac
export PYTHONPATH=src
python -m uvicorn honeypot.main:create_app --factory --reload
```

6. **Access the API**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

### Option 3: Cloud Deployment ☁️

#### Google Cloud Run

1. **Install gcloud CLI**
```bash
# Follow: https://cloud.google.com/sdk/docs/install
```

2. **Authenticate**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

3. **Build and deploy**
```bash
# Build
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/agentic-honeypot

# Deploy
gcloud run deploy agentic-honeypot \
  --image gcr.io/YOUR_PROJECT_ID/agentic-honeypot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENCRYPTION_KEY=your_key,GEMINI_API_KEY=your_key
```

#### Railway.app

1. **Create account** at https://railway.app
2. **Connect GitHub repo**
3. **Add environment variables** in dashboard
4. **Deploy automatically**

#### Render.com

1. **Create account** at https://render.com
2. **New Web Service** → Connect repo
3. **Configure**:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn honeypot.main:create_app --factory --host 0.0.0.0 --port $PORT`
4. **Add environment variables**
5. **Deploy**

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ENCRYPTION_KEY` | Fernet encryption key | `DGRP2s9PsfDib7V9rKaa4Dld-DfTaqPiCkIJ3Y1EOWQ=` |
| `API_KEYS` | List of valid API keys | `["key1", "key2"]` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `GUVI_CALLBACK_URL` | Callback endpoint | `https://hackathon.guvi.in/api/...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (fallback) | None |
| `DEFAULT_LLM_PROVIDER` | LLM provider to use | `gemini` |
| `DATABASE_URL` | Database connection string | `sqlite:///honeypot.db` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FORMAT` | Log format | `json` |
| `SESSION_TIMEOUT` | Session timeout (seconds) | `3600` |
| `RESPONSE_TIMEOUT` | Response timeout (seconds) | `30` |

---

## Secrets Management

### Production Best Practices

1. **Never commit `.env` to git**
```bash
# Already in .gitignore
.env
```

2. **Use secret management services**
- Google Secret Manager
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault

3. **Generate secure keys**
```bash
# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generate API key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Monitoring & Logging

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "service": "agentic-honeypot"
}
```

### Logs

**Docker**:
```bash
docker-compose logs -f honeypot
```

**Local**:
- Logs output to stdout
- Structured JSON format in production
- Human-readable format in development

### Metrics

Monitor these endpoints:
- `/health` - Service health
- `/docs` - API documentation
- Request logs for performance tracking

---

## Scaling

### Horizontal Scaling

1. **Load Balancer** (nginx, HAProxy)
2. **Multiple instances** behind load balancer
3. **Shared database** (PostgreSQL, MySQL)
4. **Redis** for session storage

### Vertical Scaling

- Increase CPU/Memory allocation
- Optimize worker count
- Tune database connections

---

## Troubleshooting

### Common Issues

#### 1. "Module not found" errors
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=src  # Linux/Mac
$env:PYTHONPATH='src'  # Windows
```

#### 2. "Invalid encryption key"
```bash
# Generate new key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

#### 3. "Connection refused"
- Check if port 8000 is available
- Verify firewall settings
- Check if service is running

#### 4. "API key invalid"
- Verify API_KEYS in .env
- Check x-api-key header in requests

#### 5. "No AI response"
- Verify GEMINI_API_KEY is set
- Check API quota/limits
- Review logs for errors

---

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Set strong API keys
- [ ] Rotate encryption keys regularly
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Use secrets management
- [ ] Enable logging and monitoring
- [ ] Regular security updates
- [ ] Backup database regularly

---

## Performance Tuning

### Uvicorn Workers

```bash
# Production with multiple workers
uvicorn honeypot.main:create_app --factory \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info
```

### Database Optimization

```python
# Use connection pooling
DATABASE_URL=postgresql://user:pass@host/db?pool_size=20
```

---

## Backup & Recovery

### Database Backup

```bash
# SQLite
cp honeypot.db honeypot.db.backup

# PostgreSQL
pg_dump honeypot > backup.sql
```

### Configuration Backup

```bash
# Backup .env (securely!)
cp .env .env.backup
```

---

## Support

- **Documentation**: See README.md
- **Issues**: GitHub Issues
- **Testing**: See TESTING_GUIDE.md
- **Public Deployment**: See PUBLIC_DEPLOYMENT.md

---

**Your Agentic Honeypot is ready for deployment! 🚀**
