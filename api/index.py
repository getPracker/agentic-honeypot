import sys
import os
from http.server import BaseHTTPRequestHandler
import json
import time

# Add the src directory to the system path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

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
                "timestamp": time.time(),
                "mode": "stateless"
            }
        else:
            response = {
                "message": "Agentic Honeypot API - Stateless Mode",
                "status": "running",
                "path": self.path,
                "timestamp": time.time(),
                "endpoints": {
                    "health": "/health",
                    "process": "/api/v1/process-message (POST)"
                },
                "features": [
                    "AI Agent with Personas",
                    "Scam Detection", 
                    "Intelligence Extraction",
                    "Stateless Session Management",
                    "Full Service Integration"
                ]
            }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
    
    def do_POST(self):
        # Handle POST requests - this is the main API endpoint
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Normalize the JSON data to handle different quote characters
            normalized_data = self._normalize_json_quotes(post_data.decode('utf-8'))
            
            # Parse JSON data
            data = json.loads(normalized_data) if normalized_data else {}
            
            # Validate required fields
            if not self._validate_request_body(data):
                response = {
                    "status": "error",
                    "reply": "Invalid request body format",
                    "error_code": "INVALID_REQUEST_BODY"
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            
            # Process using stateless services
            result = self.process_with_stateless_services(data)
            
            # Return in the expected simple format for external API
            response = {
                "status": "success",
                "reply": result.get("reply", "I didn't understand that.")
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Raw data: {post_data}")
            response = {
                "status": "error",
                "reply": "Invalid JSON data received",
                "error_code": "INVALID_REQUEST_BODY"
            }
        except Exception as e:
            print(f"Processing error: {e}")
            response = {
                "status": "error", 
                "reply": f"Processing error: {str(e)}",
                "error_code": "PROCESSING_ERROR"
            }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
    
    def process_with_stateless_services(self, data):
        """Process using the stateless honeypot services."""
        try:
            # Import the stateless services
            from honeypot.services.stateless_orchestrator import StatelessMessageProcessor
            from honeypot.models.core import MessageRequest, Message
            from datetime import datetime, timezone
            
            # Create the stateless processor
            processor = StatelessMessageProcessor()
            
            # Convert the incoming data to our internal format
            message_data = data.get("message", {})
            message = Message(
                sender=message_data.get("sender", "scammer"),
                text=message_data.get("text", ""),
                timestamp=self._parse_timestamp(message_data.get("timestamp")),
                message_id=message_data.get("message_id", f"msg_{int(time.time())}")
            )
            
            # Create the request
            request = MessageRequest(
                session_id=data.get("sessionId", f"session_{int(time.time())}"),
                message=message,
                conversation_history=data.get("conversationHistory", []),
                metadata=data.get("metadata", {})
            )
            
            # Process the message using the stateless orchestrator
            import asyncio
            
            # Handle async processing
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            response = loop.run_until_complete(processor.process_message(request))
            
            # Return comprehensive result
            return {
                "reply": response.agent_response or "I'm sorry, I didn't understand that.",
                "scam_detected": response.scam_detected,
                "intelligence": response.extracted_intelligence,
                "metrics": {
                    "conversation_duration": response.engagement_metrics.conversation_duration,
                    "message_count": response.engagement_metrics.message_count,
                    "engagement_quality": response.engagement_metrics.engagement_quality,
                    "intelligence_score": response.engagement_metrics.intelligence_score
                },
                "session_id": response.session_id,
                "notes": response.agent_notes
            }
                
        except ImportError as e:
            print(f"Import error: {e}")
            # Fallback to simple response
            return self.generate_fallback_response(data)
        except Exception as e:
            print(f"Processing error: {e}")
            # Fallback to simple response
            return self.generate_fallback_response(data)
    
    def _parse_timestamp(self, timestamp_data):
        """Parse timestamp from various formats."""
        if isinstance(timestamp_data, (int, float)):
            # Assume Unix timestamp in milliseconds
            return datetime.fromtimestamp(timestamp_data / 1000, tz=timezone.utc)
        elif isinstance(timestamp_data, str):
            try:
                # Try ISO format
                return datetime.fromisoformat(timestamp_data.replace('Z', '+00:00'))
            except ValueError:
                pass
        
        # Fallback to current time
        return datetime.now(timezone.utc)
    
    def generate_fallback_response(self, data):
        """Generate a simple fallback response when services are not available."""
        message_data = data.get("message", {})
        message_text = message_data.get("text", "").lower()
        
        # Simple rule-based responses as fallback
        if "bank" in message_text or "account" in message_text:
            responses = [
                "Oh no! What happened to my account? What do I need to do?",
                "I'm really worried about this. How can I verify my account?",
                "Please help me fix this immediately. What information do you need?"
            ]
        elif "lottery" in message_text or "won" in message_text:
            responses = [
                "Really? I can't believe I won! What do I need to do to claim it?",
                "This is amazing! How much did I win? What's the next step?",
                "I'm so excited! Please tell me how to collect my prize."
            ]
        elif "urgent" in message_text or "immediate" in message_text:
            responses = [
                "Oh my goodness, I don't want to miss this! What should I do right now?",
                "I'm available now! Please tell me exactly what I need to do.",
                "I'm ready to act immediately! What's the first step?"
            ]
        else:
            responses = [
                "I'm concerned about this. Can you please help me understand what to do?",
                "This sounds important. What information do you need from me?",
                "I want to resolve this quickly. Please tell me the next steps."
            ]
        
        import random
        return {"reply": random.choice(responses)}
    
    def _validate_request_body(self, data):
        """Validate the request body has required structure."""
        if not isinstance(data, dict):
            return False
        
        # Check for required fields
        if "message" not in data:
            return False
        
        message = data.get("message", {})
        if not isinstance(message, dict):
            return False
        
        # Check message has required fields
        if "text" not in message:
            return False
        
        # Optional but recommended fields
        if "sessionId" not in data:
            print("Warning: sessionId missing from request")
        
        return True
    
    def _normalize_json_quotes(self, json_string):
        """
        Normalize different types of quotes in JSON to standard double quotes.
        
        Handles:
        - Curly quotes: " " → " "
        - Single quotes: ' → "
        - Other Unicode quotes
        """
        if not json_string:
            return json_string
        
        # Dictionary of problematic quotes to replace
        quote_replacements = {
            # Curly double quotes
            '"': '"',  # Left double quotation mark
            '"': '"',  # Right double quotation mark
            
            # Curly single quotes  
            ''': "'",  # Left single quotation mark
            ''': "'",  # Right single quotation mark
            
            # Other Unicode quotes
            '‚': "'",  # Single low-9 quotation mark
            '„': '"',  # Double low-9 quotation mark
            '‹': "'",  # Single left-pointing angle quotation mark
            '›': "'",  # Single right-pointing angle quotation mark
            '«': '"',  # Left-pointing double angle quotation mark
            '»': '"',  # Right-pointing double angle quotation mark
        }
        
        # Replace all problematic quotes
        normalized = json_string
        for bad_quote, good_quote in quote_replacements.items():
            normalized = normalized.replace(bad_quote, good_quote)
        
        # Additional safety: try to fix common single quote JSON issues
        # This is more aggressive and might need adjustment
        try:
            # Test if it's valid JSON now
            json.loads(normalized)
            return normalized
        except json.JSONDecodeError:
            # Try converting single quotes to double quotes for JSON keys/values
            # This is a simple heuristic and might not work for all cases
            try:
                # Replace single quotes around keys and values with double quotes
                import re
                # Pattern to match single-quoted strings (simple version)
                pattern = r"'([^']*?)'"
                normalized = re.sub(pattern, r'"\1"', normalized)
                
                # Test again
                json.loads(normalized)
                return normalized
            except:
                # Return original if all normalization attempts fail
                return json_string
        
        return normalized

