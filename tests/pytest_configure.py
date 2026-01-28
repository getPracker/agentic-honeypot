"""Pytest configuration for test suite."""

import os
import sys

# Set up environment variables before any imports
# Use a valid Fernet key for all tests
os.environ['DATABASE_URL'] = "sqlite:///test.db"
os.environ['ENCRYPTION_KEY'] = "DGRP2s9PsfDib7V9rKaa4Dld-DfTaqPiCkIJ3Y1EOWQ="
os.environ['API_KEYS'] = '["test-key"]'

# Ensure src is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
