#!/usr/bin/env python3
"""
Local HTTP server that mimics Vercel's serverless function behavior.
This allows testing the exact same code locally that runs on Vercel.
"""

import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time

# Add the src directory to the system path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the same handler class used in Vercel
from api.index import handler as VercelHandler

class LocalServerHandler(VercelHandler):
    """
    Extends the Vercel handler to work with local HTTP server.
    Uses the exact same logic as api/index.py
    """
    
    def log_message(self, format, *args):
        """Override to provide better logging."""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_server(host='localhost', port=8000):
    """Run the local server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, LocalServerHandler)
    
    print(f"🚀 Local Honeypot Server Starting...")
    print(f"📍 Server running at: http://{host}:{port}")
    print(f"🔍 Health check: http://{host}:{port}/health")
    print(f"📡 API endpoint: http://{host}:{port}/api/v1/process-message")
    print(f"📚 Same behavior as Vercel deployment")
    print(f"⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        httpd.server_close()

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run server
    run_server()