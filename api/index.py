import sys
import os
from http.server import BaseHTTPRequestHandler
import json
import time
from typing import List
from datetime import datetime, timezone

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
        
        # Get headers
        content_type = self.headers.get('Content-Type', '')
        api_key = self.headers.get('x-api-key', '')
        
        # Debug logging
        print(f"📥 Received POST request:")
        print(f"   Content-Length: {content_length}")
        print(f"   Content-Type: {content_type}")
        print(f"   x-api-key: {'***' + api_key[-4:] if len(api_key) > 4 else 'Not provided'}")
        print(f"   Raw data length: {len(post_data)}")
        print(f"   Raw data (first 200 chars): {post_data[:200]}")
        
        # Validate Content-Type
        if content_type and not content_type.startswith('application/json'):
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "error",
                "reply": "Content-Type must be application/json",
                "error_code": "INVALID_CONTENT_TYPE"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        # Validate API key (if provided in environment)
        expected_api_keys = self._get_expected_api_keys()
        if expected_api_keys and api_key not in expected_api_keys:
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "error",
                "reply": "Invalid or missing API key",
                "error_code": "INVALID_API_KEY"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Decode raw data
            raw_string = post_data.decode('utf-8')
            print(f"📝 Decoded string: {raw_string[:200]}...")
            
            # Check for problematic characters
            problematic_chars = []
            for i, char in enumerate(raw_string):
                if ord(char) > 127:
                    problematic_chars.append(f"pos {i}: '{char}' (U+{ord(char):04X})")
            
            if problematic_chars:
                print(f"⚠️  Non-ASCII characters found: {problematic_chars[:5]}")
            
            # Normalize the JSON data to handle different quote characters
            normalized_data = self._normalize_json_quotes(raw_string)
            print(f"🔧 Normalized data: {normalized_data[:200]}...")
            
            # Parse JSON data
            data = json.loads(normalized_data) if normalized_data else {}
            print(f"✅ JSON parsed successfully: {list(data.keys())}")
            
            # Validate required fields
            if not self._validate_request_body(data):
                print("❌ Request body validation failed")
                response = {
                    "status": "error",
                    "reply": "Invalid request body format",
                    "error_code": "INVALID_REQUEST_BODY"
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            
            print("✅ Request body validation passed")
            
            print("🎯 [MAIN] Calling process_with_stateless_services...")
            # Process using stateless services
            result = self.process_with_stateless_services(data)
            print(f"✅ [MAIN] process_with_stateless_services returned: {type(result)}")
            print(f"📋 [MAIN] Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            print("🔧 [MAIN] Building external API response...")
            # Return in the expected simple format for external API
            response = {
                "status": "success",
                "reply": result.get("reply", "I didn't understand that.")
            }
            print(f"✅ [MAIN] Final response: {response}")
            print("🎉 [MAIN] POST request processing completed successfully")

            print(response)
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"   Error position: {e.pos}")
            print(f"   Context: '{raw_string[max(0, e.pos-20):e.pos+20]}'")
            response = {
                "status": "error",
                "reply": "Invalid JSON data received",
                "error_code": "INVALID_REQUEST_BODY"
            }
        except UnicodeDecodeError as e:
            print(f"❌ Unicode decode error: {e}")
            response = {
                "status": "error",
                "reply": "Invalid character encoding",
                "error_code": "INVALID_REQUEST_BODY"
            }
        except Exception as e:
            print(f"❌ Processing error: {e}")
            import traceback
            traceback.print_exc()
            response = {
                "status": "error", 
                "reply": f"Processing error: {str(e)}",
                "error_code": "PROCESSING_ERROR"
            }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
    
    def process_with_stateless_services(self, data):
        """Process using the stateless honeypot services."""
        print("🚀 [LINE 1] Starting process_with_stateless_services")
        print(f"📥 [LINE 2] Input data keys: {list(data.keys())}")
        
        try:
            print("📦 [LINE 5] Attempting to import stateless services...")
            # Import the stateless services
            from honeypot.services.stateless_orchestrator import StatelessMessageProcessor
            from honeypot.models.core import MessageRequest, Message
            from datetime import datetime, timezone
            print("✅ [LINE 10] Successfully imported stateless services")
            
            print("🏗️ [LINE 12] Creating StatelessMessageProcessor...")
            # Create the stateless processor
            processor = StatelessMessageProcessor()
            print("✅ [LINE 15] StatelessMessageProcessor created successfully")
            
            print("🔄 [LINE 17] Converting incoming data to internal format...")
            # Convert the incoming data to our internal format
            message_data = data.get("message", {})
            print(f"📝 [LINE 20] Message data: {message_data}")
            
            message = Message(
                sender=message_data.get("sender", "scammer"),
                text=message_data.get("text", ""),
                timestamp=self._parse_timestamp(message_data.get("timestamp")),
                message_id=message_data.get("message_id", f"msg_{int(time.time())}")
            )
            print(f"✅ [LINE 28] Message object created: sender={message.sender}, text='{message.text[:50]}...'")
            
            # Create the request
            request = MessageRequest(
                session_id=data.get("sessionId", f"session_{int(time.time())}"),
                message=message,
                conversation_history=data.get("conversationHistory", []),
                metadata=data.get("metadata", {})
            )
            print(f"✅ [LINE 37] MessageRequest created: session_id={request.session_id}")
            print(f"📊 [LINE 38] Conversation history length: {len(request.conversation_history)}")
            
            print("⚙️ [LINE 40] Setting up async processing...")
            # Process the message using the stateless orchestrator
            import asyncio
            
            # Handle async processing
            try:
                loop = asyncio.get_event_loop()
                print("🔄 [LINE 47] Using existing event loop")
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                print("🆕 [LINE 51] Created new event loop")
            
            print("🎯 [LINE 53] Calling processor.process_message()...")
            response = loop.run_until_complete(processor.process_message(request))
            print("✅ [LINE 55] processor.process_message() completed successfully")
            
            print(f"📋 [LINE 57] Response object attributes:")
            print(f"   - status: {response.status}")
            print(f"   - scam_detected: {response.scam_detected}")
            print(f"   - agent_response: {response.agent_response[:100] if response.agent_response else 'None'}...")
            print(f"   - session_id: {response.session_id}")
            
            print("🔧 [LINE 64] Building comprehensive result...")
            # Return comprehensive result
            result = {
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
            
            print(f"✅ [LINE 78] Final result created:")
            print(f"   - reply: '{result['reply'][:100]}...'")
            print(f"   - scam_detected: {result['scam_detected']}")
            print(f"   - intelligence keys: {list(result['intelligence'].keys()) if result['intelligence'] else 'None'}")
            print(f"   - metrics: {result['metrics']}")
            
            print("🎉 [LINE 84] process_with_stateless_services completed successfully")
            return result
                
        except ImportError as e:
            print(f"❌ [LINE 88] Import error: {e}")
            print("🔄 [LINE 89] Falling back to simple response")
            # Fallback to simple response
            fallback_result = self.generate_fallback_response(data)
            print(f"✅ [LINE 92] Fallback result: {fallback_result}")
            return fallback_result
        except Exception as e:
            print(f"❌ [LINE 95] Processing error: {e}")
            print("📍 [LINE 96] Exception details:")
            import traceback
            traceback.print_exc()
            print("🔄 [LINE 99] Falling back to simple response")
            # Fallback to simple response
            fallback_result = self.generate_fallback_response(data)
            print(f"✅ [LINE 102] Fallback result: {fallback_result}")
            return fallback_result
    
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
    
    def _get_expected_api_keys(self):
        """Get expected API keys from environment."""
        import os
        import json
        
        # Get API keys from environment
        api_keys_env = os.getenv('API_KEYS', '')
        
        if not api_keys_env:
            # No API keys configured - allow all requests (for testing)
            return None
        
        try:
            # Parse JSON array of API keys
            api_keys = json.loads(api_keys_env)
            if isinstance(api_keys, list):
                return api_keys
            else:
                print(f"⚠️ API_KEYS should be a JSON array, got: {type(api_keys)}")
                return None
        except json.JSONDecodeError:
            print(f"⚠️ Invalid API_KEYS format: {api_keys_env}")
            return None
    
    def _normalize_json_quotes(self, json_string):
        """
        Normalize different types of quotes in JSON to standard double quotes.
        
        Handles quotes by ASCII/Unicode code points that look similar but aren't standard.
        """
        if not json_string:
            return json_string
        
        # Convert to list for character-by-character processing
        chars = list(json_string)
        
        for i, char in enumerate(chars):
            char_code = ord(char)
            
            # Replace any quote-like character with standard double quote (ASCII 34)
            if char_code in [
                # Standard quotes
                34,   # " (standard double quote)
                39,   # ' (standard single quote)
                
                # Unicode quote variants that look like normal quotes
                8220, # " (left double quotation mark)
                8221, # " (right double quotation mark)
                8216, # ' (left single quotation mark) 
                8217, # ' (right single quotation mark)
                
                # Other quote-like characters
                96,   # ` (grave accent)
                180,  # ´ (acute accent)
                8242, # ′ (prime)
                8243, # ″ (double prime)
                
                # Fullwidth quotes (from some input methods)
                65282, # ＂ (fullwidth quotation mark)
                
                # Additional Unicode quotes
                8218, # ‚ (single low-9 quotation mark)
                8222, # „ (double low-9 quotation mark)
                8249, # ‹ (single left-pointing angle quotation mark)
                8250, # › (single right-pointing angle quotation mark)
                171,  # « (left-pointing double angle quotation mark)
                187,  # » (right-pointing double angle quotation mark)
            ]:
                # Replace with standard double quote for JSON
                chars[i] = '"'
                print(f"🔧 Replaced quote-like char at pos {i}: U+{char_code:04X} → U+0022")
        
        normalized = ''.join(chars)
        
        # Test if the normalization worked
        try:
            json.loads(normalized)
            print("✅ JSON normalization successful")
            return normalized
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON still invalid after normalization: {e}")
            
            # Try more aggressive fixes
            try:
                # Fix common JSON issues
                fixed = self._fix_common_json_issues(normalized)
                json.loads(fixed)
                print("✅ JSON fixed with aggressive normalization")
                return fixed
            except:
                print("❌ Could not fix JSON, returning original")
                return json_string
    
    def _fix_common_json_issues(self, json_string):
        """Apply more aggressive JSON fixes."""
        import re
        
        fixed = json_string
        
        # Fix unescaped quotes in string values
        # This is a simple heuristic - might need refinement
        
        # Fix trailing commas
        fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
        
        # Fix single quotes around property names (if any remain)
        fixed = re.sub(r"'([^']*?)'(\s*:)", r'"\1"\2', fixed)
        
        # Fix unquoted property names
        fixed = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', fixed)
        
        return fixed

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, x-api-key')
        self.send_header('Access-Control-Max-Age', '86400')  # 24 hours
        self.end_headers()
        return