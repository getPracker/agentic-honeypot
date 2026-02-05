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
            from honeypot.models.core import MessageRequest, Message, RequestMetadata
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
            
            # Fix conversation history - convert to proper Message objects
            print("🔧 [LINE 31] Processing conversation history...")
            conversation_history = data.get("conversationHistory", [])
            fixed_history = []
            
            for i, hist_msg in enumerate(conversation_history):
                # Ensure all required fields are present
                if "message_id" not in hist_msg:
                    hist_msg["message_id"] = f"hist_{i}_{int(time.time())}"
                    print(f"   🔧 Added message_id to history item {i}: {hist_msg['message_id']}")
                
                # Ensure timestamp is properly formatted
                if "timestamp" in hist_msg:
                    parsed_timestamp = self._parse_timestamp(hist_msg["timestamp"])
                else:
                    parsed_timestamp = datetime.now(timezone.utc)
                    print(f"   🔧 Added missing timestamp to history item {i}")
                
                # Create proper Message object
                try:
                    message_obj = Message(
                        sender=hist_msg.get("sender", "unknown"),
                        text=hist_msg.get("text", ""),
                        timestamp=parsed_timestamp,
                        message_id=hist_msg["message_id"]
                    )
                    fixed_history.append(message_obj)
                    print(f"   ✅ Created Message object for history item {i}")
                except Exception as e:
                    print(f"   ❌ Failed to create Message object for history item {i}: {e}")
                    # Skip invalid history items
                    continue
            print(f"✅ [LINE 44] Fixed conversation history: {len(fixed_history)} messages")
            
            print("⚙️ [LINE 46] Setting up async processing...")
            # Create proper metadata object
            metadata_dict = data.get("metadata", {})
            metadata = RequestMetadata(
                channel=metadata_dict.get("channel", "Unknown"),
                language=metadata_dict.get("language", "English"),
                locale=metadata_dict.get("locale", "US")
            )
            print(f"✅ [LINE 54] Created RequestMetadata: {metadata.channel}, {metadata.language}, {metadata.locale}")
            
            # Create the request
            request = MessageRequest(
                session_id=data.get("sessionId", f"session_{int(time.time())}"),
                message=message,
                conversation_history=fixed_history,
                metadata=metadata
            )
            print(f"✅ [LINE 62] MessageRequest created: session_id={request.session_id}")
            print(f"📊 [LINE 63] Conversation history length: {len(request.conversation_history)}")
            
            print("⚙️ [LINE 65] Setting up async processing...")
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
        """Generate a contextual fallback response when services are not available."""
        print("🔄 [FALLBACK] Generating fallback response...")
        
        message_data = data.get("message", {})
        message_text = message_data.get("text", "").lower()
        print(f"📝 [FALLBACK] Message text: '{message_text}'")
        
        # More sophisticated fallback responses based on content analysis
        
        # Bank/Account related - show concern and ask for help
        if any(word in message_text for word in ["bank", "account", "blocked", "suspended", "verify", "kyc"]):
            responses = [
                "Oh no! What happened to my account? I just used it yesterday. What do I need to do to fix this?",
                "This is very concerning. Can you tell me exactly what's wrong with my account?",
                "I'm really worried about this. How can I verify my account? What information do you need?",
                "Please help me understand what verification you need. I don't want to lose access to my money.",
                "Is this really from my bank? I want to resolve this immediately. What should I do first?"
            ]
            category = "bank/account"
        
        # UPI/Payment related - show confusion but willingness to learn
        elif any(word in message_text for word in ["upi", "paytm", "gpay", "payment", "transfer", "qr"]):
            responses = [
                "I'm not very good with these payment apps. Can you guide me through this step by step?",
                "My son set up UPI for me but I'm still confused. What exactly do you need me to do?",
                "I want to make sure I do this correctly. Can you explain how this works?",
                "What UPI ID are you talking about? I'm not sure what that means. Can you help me find it?",
                "Is this safe? I've heard about people having problems with online payments."
            ]
            category = "upi/payment"
        
        # Password/PIN/OTP related - show confusion about security
        elif any(word in message_text for word in ["password", "pin", "otp", "code", "cvv"]):
            responses = [
                "Is that the number on the back of my card? The print is so small, I can barely read it.",
                "I have so many passwords, I get confused. Which specific one do you need?",
                "I just got a message with some numbers. Is that what you're asking for?",
                "I'm worried about sharing this information. How do I know you're really from the bank?",
                "My grandson usually helps me with these codes. Should I call him first?"
            ]
            category = "security/codes"
        
        # Investment/Money opportunities - show interest and ask questions
        elif any(word in message_text for word in ["invest", "profit", "earn", "money", "scheme", "opportunity", "return"]):
            responses = [
                "That sounds wonderful! I've been looking for ways to grow my savings. Can you tell me more?",
                "How much money do I need to start? I have some savings but I'm not sure how much to invest.",
                "This sounds very interesting. Can you explain exactly how this works?",
                "I'm definitely interested! What do I need to do to get started with this opportunity?",
                "My late husband always said to be careful with investments, but this sounds legitimate. Tell me more."
            ]
            category = "investment"
        
        # Lottery/Prize related - show excitement and ask for details
        elif any(word in message_text for word in ["won", "winner", "lottery", "prize", "congratulations", "claim"]):
            responses = [
                "Really? I can't believe I won something! I never win anything. What exactly did I win?",
                "This is so exciting! How much is the prize? What do I need to do to claim it?",
                "I don't remember entering any lottery. Are you sure this is for me? What's my winning number?",
                "I'm so happy! Please tell me exactly what I need to do to get my prize.",
                "This is amazing news! How did you get my number? What lottery is this from?"
            ]
            category = "lottery/prize"
        
        # Tech Support related - show worry and gratitude
        elif any(word in message_text for word in ["computer", "virus", "infected", "microsoft", "support", "error", "malware"]):
            responses = [
                "Oh dear! I knew something was wrong with my computer. It's been running so slowly lately.",
                "I'm not good with computers at all. Can you please help me fix this problem?",
                "My computer has been acting very strange. What kind of virus do I have?",
                "Should I be worried? I have all my important photos and documents on this computer.",
                "Thank goodness you called! I was wondering who to contact about these computer problems."
            ]
            category = "tech_support"
        
        # Questions that need specific responses
        elif any(word in message_text for word in ["what", "how", "when", "where", "why", "can you", "do you"]):
            if "name" in message_text:
                responses = ["My name is Margaret Thompson. What do you need my name for exactly?"]
            elif "address" in message_text:
                responses = ["I live at 123 Oak Street, Apartment 4B. Do you need my complete address for this?"]
            elif "phone" in message_text or "number" in message_text:
                responses = ["My phone number? It's the one you just called me on. Do you need me to repeat it?"]
            elif "age" in message_text:
                responses = ["I'm 72 years old. Why do you need to know my age for this?"]
            else:
                responses = [
                    "I'm not sure I understand the question. Can you explain it differently?",
                    "Could you be more specific? I want to make sure I give you the right information.",
                    "I'm a bit confused by what you're asking. Can you break it down for me?"
                ]
            category = "questions"
        
        # Urgent/Time pressure - show willingness to act quickly
        elif any(word in message_text for word in ["urgent", "immediate", "now", "today", "hurry", "quick", "expire"]):
            responses = [
                "Oh my! I don't want to miss this opportunity. I'm ready to do whatever you need right now.",
                "This sounds very urgent. I'm available right now. What should I do first?",
                "I'm worried about waiting too long. Please tell me exactly what I need to do.",
                "I don't want any problems with my account. I'm ready to act immediately. Guide me through it.",
                "Time is important, I understand. I'm listening carefully to your instructions."
            ]
            category = "urgent"
        
        # Generic but engaging responses for unclear messages
        else:
            responses = [
                "I'm sorry, I didn't quite understand that. Can you explain it more clearly?",
                "Could you repeat that? I want to make sure I understand what you need from me.",
                "I'm a bit confused. Can you tell me more about what this is regarding?",
                "This sounds important. Can you break it down step by step for me?",
                "I want to help, but I need you to explain this better. What exactly are you asking?",
                "I'm trying to follow along. Can you give me more details about what you need?",
                "Let me make sure I understand correctly. Are you saying that my account has a problem?",
                "I'm listening carefully. Can you be more specific about what I need to do?"
            ]
            category = "generic_engagement"
        
        selected_response = random.choice(responses)
        
        print(f"🎯 [FALLBACK] Category: {category}")
        print(f"✅ [FALLBACK] Selected response: '{selected_response}'")
        
        result = {"reply": selected_response}
        print(f"📋 [FALLBACK] Final fallback result: {result}")
        return result
    
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