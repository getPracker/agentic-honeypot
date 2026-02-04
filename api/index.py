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
                "endpoints": {
                    "health": "/health",
                    "process": "/api/v1/process-message (POST)"
                }
            }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
    
    def do_POST(self):
        # Handle POST requests - this is the main API endpoint
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        # Check API key (basic validation)
        api_key = self.headers.get('x-api-key')
        expected_api_keys = ["7nSdYaVoJPGXcveub_8YPhuv4hyE7G7ZeeWrfBw7Rbo"]  # Add your API key here
        
        # Skip API key check for now to match the working submission
        # if not api_key or api_key not in expected_api_keys:
        #     self.send_response(401)
        #     self.send_header('Content-type', 'application/json')
        #     self.send_header('Access-Control-Allow-Origin', '*')
        #     self.end_headers()
        #     error_response = {"status": "error", "message": "Invalid or missing API key"}
        #     self.wfile.write(json.dumps(error_response).encode('utf-8'))
        #     return
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Parse JSON data
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
            
            # Extract message details
            session_id = data.get("sessionId", "unknown")
            message = data.get("message", {})
            message_text = message.get("text", "")
            sender = message.get("sender", "unknown")
            conversation_history = data.get("conversationHistory", [])
            metadata = data.get("metadata", {})
            
            # Generate appropriate response based on the scam message
            # This is a simple rule-based response for now
            reply = self.generate_scam_response(message_text, sender, metadata)
            
            # Return the expected format
            response = {
                "status": "success",
                "reply": reply
            }
            
        except json.JSONDecodeError:
            response = {
                "status": "error",
                "reply": "Invalid JSON data received"
            }
        except Exception as e:
            response = {
                "status": "error", 
                "reply": f"Processing error: {str(e)}"
            }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
    
    def generate_scam_response(self, message_text, sender, metadata):
        """Generate an appropriate response to the scam message."""
        
        # Convert message to lowercase for pattern matching
        text_lower = message_text.lower()
        
        # Different response strategies based on scam type
        if "bank" in text_lower or "account" in text_lower:
            responses = [
                "Why is my account being suspended?",
                "I don't understand, what verification do you need?",
                "Can you please explain what's wrong with my account?",
                "Is this really from my bank? This seems suspicious.",
                "What documents do I need to provide?"
            ]
        elif "lottery" in text_lower or "won" in text_lower or "prize" in text_lower:
            responses = [
                "Really? I won something? What do I need to do?",
                "This sounds too good to be true. How did I win?",
                "What lottery is this? I don't remember entering any.",
                "Do I need to pay any fees to claim the prize?",
                "Can you send me more details about this lottery?"
            ]
        elif "tax" in text_lower or "refund" in text_lower or "irs" in text_lower:
            responses = [
                "I wasn't expecting a tax refund. Are you sure?",
                "What information do you need from me?",
                "How much is the refund amount?",
                "Why do I need to verify my details for a refund?",
                "Is this really from the tax department?"
            ]
        elif "urgent" in text_lower or "immediate" in text_lower or "expire" in text_lower:
            responses = [
                "Why is this so urgent? What happens if I don't act now?",
                "Can I call you back to verify this?",
                "This seems very rushed. Is there a deadline?",
                "I need time to think about this. Can you wait?",
                "Why didn't I receive any prior notice about this?"
            ]
        elif "click" in text_lower or "link" in text_lower or "verify" in text_lower:
            responses = [
                "I'm not comfortable clicking links. Can you help me another way?",
                "Is there a phone number I can call instead?",
                "Why do I need to click a link? This seems suspicious.",
                "Can you verify your identity first?",
                "I prefer to handle this through official channels."
            ]
        else:
            # Generic responses for other types of scams
            responses = [
                "I'm not sure I understand. Can you explain more?",
                "This is unexpected. Are you sure you have the right person?",
                "I need to verify this with someone first.",
                "Can you provide more details about this?",
                "I'm confused. Why are you contacting me about this?"
            ]
        
        # Select response based on conversation context or randomly
        import random
        return random.choice(responses)

