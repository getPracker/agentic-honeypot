from http.server import BaseHTTPRequestHandler
import json
import time
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Simple health check response
        if self.path == '/health':
            response = {
                "status": "healthy", 
                "service": "agentic-honeypot",
                "timestamp": time.time()
            }
        else:
            response = {
                "message": "Agentic Honeypot API",
                "status": "running",
                "path": self.path,
                "timestamp": time.time(),
                "note": "Full application loading disabled due to dependency issues"
            }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
    
    def do_POST(self):
        # Handle POST requests
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Parse JSON data
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
            
            response = {
                "message": "POST request received",
                "path": self.path,
                "data_received": bool(post_data),
                "timestamp": time.time(),
                "status": "success",
                "note": "This is a minimal endpoint. Full AI processing not available due to dependency issues."
            }
            
        except json.JSONDecodeError:
            response = {
                "error": "Invalid JSON data",
                "timestamp": time.time(),
                "status": "error"
            }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return

