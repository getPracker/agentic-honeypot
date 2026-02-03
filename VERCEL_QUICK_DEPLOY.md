# Quick Vercel Deployment Guide

## Current Status
The application has been configured for Vercel deployment with a **minimal working setup** due to dependency complexity.

## What Works Now
- ✅ `/health` - Health check endpoint
- ✅ `/ping` - Simple ping endpoint  
- ✅ `/hello` - Test endpoint
- ✅ `/process` - Placeholder for AI processing
- ✅ Basic HTTP handling (GET/POST)

## What's Limited
- ⚠️ Full AI agent functionality (due to `google-generativeai` import issues)
- ⚠️ Complex FastAPI application structure

## Deploy Steps

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Fix Vercel deployment configuration"
   git push
   ```

2. **Deploy to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Vercel will auto-detect the configuration

3. **Set Environment Variables** in Vercel dashboard:
   ```
   ENCRYPTION_KEY=your-encryption-key
   API_KEYS=["your-api-key"]
   GEMINI_API_KEY=your-gemini-key
   GUVI_CALLBACK_URL=https://hackathon.guvi.in/api/updateHoneyPotFinalResult
   DEFAULT_LLM_PROVIDER=gemini
   LOG_LEVEL=INFO
   ```

## Test Endpoints

After deployment, test these URLs:

```bash
# Health check
curl https://your-app.vercel.app/health

# Ping test
curl https://your-app.vercel.app/ping

# Hello test
curl https://your-app.vercel.app/hello

# Process endpoint (POST)
curl -X POST https://your-app.vercel.app/process \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "message": {"text": "Hello"}}'
```

## Next Steps

To enable full AI functionality:

1. **Fix dependency issues** - Ensure all Python packages install correctly
2. **Gradual loading** - Load AI components only when needed
3. **Error handling** - Better fallback mechanisms

## Alternative: Docker Deployment

For full functionality, consider deploying with Docker on:
- Railway
- Render  
- Google Cloud Run
- AWS ECS

The Docker configuration is already ready in your project.