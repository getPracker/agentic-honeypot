# Vercel Deployment Guide - Agentic Honeypot

This guide explains how to deploy the Agentic Honeypot application to Vercel as a serverless Python function.

## Prerequisites

- A [Vercel](https://vercel.com) account
- The project pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Configuration Files (Already Created)

The following files have been added to your project to enable Vercel deployment:

1.  `vercel.json` - Configures the build and routing for Python.
2.  `api/index.py` - The entry point that exposes the FastAPI application to Vercel.

## Deployment Steps

### 1. Push to Git

Ensure your latest changes (including `vercel.json` and `api/index.py`) are committed and pushed to your repository.

```bash
git add .
git commit -m "Add Vercel deployment configuration"
git push
```

### 2. Import into Vercel

1.  Log in to your Vercel Dashboard.
2.  Click **"Add New..."** -> **"Project"**.
3.  Import your repository (`agentic-honeypot`).
4.  Vercel should automatically detect the settings.
    *   **Framework Preset**: Other
    *   **Root Directory**: `./`

### 3. Configure Environment Variables (Crucial)

Before clicking "Deploy", you **MUST** add the environment variables. Expand the **"Environment Variables"** section and add the following:

| Key | Value (Example/Description) |
|-----|-----------------------------|
| `ENCRYPTION_KEY` | `DGRP2s9PsfDib7V9rKaa4Dld-DfTaqPiCkIJ3Y1EOWQ=` (Use your own) |
| `API_KEYS` | `["your-secure-api-key"]` (JSON formatted array) |
| `GEMINI_API_KEY` | `AIza...` (Your Gemini API Key) |
| `GUVI_CALLBACK_URL` | `https://hackathon.guvi.in/api/updateHoneyPotFinalResult` |
| `OPENAI_API_KEY` | (Optional) Your OpenAI API Key |
| `DEFAULT_LLM_PROVIDER` | `gemini` |
| `LOG_LEVEL` | `INFO` |

**Note**: For `API_KEYS`, make sure to use valid JSON syntax (e.g., `["key1", "key2"]`).

### 4. Deploy

Click **"Deploy"**. Vercel will build your project and install dependencies from `requirements.txt`.

## Verifying Deployment

Once deployed, Vercel will give you a production URL (e.g., `https://agentic-honeypot-xyz.vercel.app`).

Test the health endpoint:
```bash
curl https://your-project-url.vercel.app/health
```

Test the processing endpoint:
```bash
curl -X POST https://your-project-url.vercel.app/api/v1/process-message \
  -H "x-api-key: your-secure-api-key" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test_1", "message": {"text": "You won lottery!", "sender": "scam", "timestamp": "2024-01-01T00:00:00Z", "message_id": "1"}, "conversation_history": [], "metadata": {}}'
```

## Troubleshooting

- **500 Internal Server Error**: Check the "Logs" tab and "Runtime Logs" in Vercel to see the Python error. deeply check if environment variables are set correctly.
- **Quota Exceeded**: If the AI doesn't respond, check your Gemini/OpenAI API quotas.
- **Module Not Found**: Ensure `requirements.txt` is updated. Vercel installs dependencies automatically from there.
