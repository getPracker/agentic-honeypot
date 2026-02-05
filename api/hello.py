from http.server import BaseHTTPRequestHandler
import json
import time

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "message": "Hello from Vercel!",
            "timestamp": time.time(),
            "status": "working"
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return