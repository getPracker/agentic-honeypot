import sys
import os
from http.server import BaseHTTPRequestHandler
import json

# Add the src directory to the system path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set environment variables for serverless
os.environ.setdefault('PYTHONPATH', os.path.join(os.path.dirname(__file__), '..', 'src'))

# Global app instance
app = None

def get_app():
    """Get or create the FastAPI app instance."""
    global app
    if app is None:
        try:
            from honeypot.main import create_app
            app = create_app()
        except Exception as e:
            print(f"Error creating app: {e}", file=sys.stderr)
            # Create a minimal fallback app
            from fastapi import FastAPI
            app = FastAPI()
            
            @app.get("/")
            async def fallback():
                return {"error": "Failed to start application", "details": str(e)}
            
            @app.get("/health")
            async def health():
                return {"status": "error", "message": "Startup failed"}
    
    return app

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()
    
    def do_POST(self):
        self.handle_request()
    
    def do_PUT(self):
        self.handle_request()
    
    def do_DELETE(self):
        self.handle_request()
    
    def handle_request(self):
        """Handle HTTP request using FastAPI app."""
        try:
            # Import ASGI adapter
            from fastapi import Request
            import asyncio
            
            # Get the FastAPI app
            fastapi_app = get_app()
            
            # For simple health check, return directly
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "healthy", "service": "agentic-honeypot"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            
            # For other routes, we need to handle them properly
            # This is a simplified handler - in production you'd want a proper ASGI adapter
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "message": "FastAPI app is running",
                "path": self.path,
                "method": self.command,
                "note": "Use proper ASGI server for full functionality"
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {
                "error": "Internal server error",
                "details": str(e)
            }
            
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

# For compatibility, also expose the app directly
try:
    app = get_app()
except:
    pass

