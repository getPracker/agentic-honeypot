from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add the src directory to the system path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read POST data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse JSON
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
            
            # Try to load the full application
            try:
                from honeypot.main import create_app
                from honeypot.models.core import MessageRequest
                
                # This would be the full processing logic
                response_data = {
                    "status": "success",
                    "message": "AI processing would happen here",
                    "session_id": data.get("session_id", "unknown"),
                    "received_message": data.get("message", {}),
                    "note": "Full AI agent not loaded due to dependency issues"
                }
                
            except ImportError as e:
                response_data = {
                    "status": "error",
                    "message": "AI dependencies not available",
                    "error": str(e),
                    "received_data": data
                }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            # Error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "status": "error",
                "message": "Internal server error",
                "error": str(e)
            }
            
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_GET(self):
        # Handle GET requests
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "message": "AI Processing Endpoint",
            "method": "POST",
            "path": "/api/v1/process-message",
            "status": "ready"
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))