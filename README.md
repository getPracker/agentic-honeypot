# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

An AI-powered security solution that automatically detects fraudulent messages, engages scammers through believable human-like conversations, and extracts valuable intelligence about scam operations.

## Features

- **Scam Detection**: Advanced NLP-based detection of various scam types
- **AI Agent Engagement**: Human-like conversation with scammers
- **Intelligence Extraction**: Structured extraction of scam-related data
- **Session Management**: Stateful conversation tracking
- **Secure API**: REST API with authentication and validation
- **Real-time Processing**: Sub-30 second response times

## Installation

```bash
pip install -e ".[dev]"
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run property-based tests
pytest -m property

# Format code
black src tests
isort src tests

# Type checking
mypy src
```

## Configuration

Copy `.env.example` to `.env` and configure the required environment variables.

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.