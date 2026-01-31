"""Tests for SessionManager service."""

import unittest
import time
from datetime import datetime
from uuid import uuid4
import sys
import os

# Set required env vars for Settings
os.environ['DATABASE_URL'] = "sqlite:///test.db"
os.environ['ENCRYPTION_KEY'] = "test_key_12345"

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeypot.services.session_manager import SessionManager
from honeypot.models.session import SessionStatus
from honeypot.models.core import Message

class TestSessionManager(unittest.TestCase):
    def test_create_session(self):
        manager = SessionManager()
        session = manager.create_session("sess_001")
        self.assertEqual(session.session_id, "sess_001")
        self.assertEqual(session.status, SessionStatus.ACTIVE)
        
        retrieved = manager.get_session("sess_001")
        self.assertEqual(retrieved, session)

    def test_create_session_generated_id(self):
        manager = SessionManager()
        session = manager.create_session()
        self.assertIsNotNone(session.session_id)
        self.assertTrue(len(session.session_id) > 0)

    def test_create_session_duplicate(self):
        manager = SessionManager()
        manager.create_session("sess_001")
        with self.assertRaises(ValueError):
            manager.create_session("sess_001")

    def test_get_nonexistent_session(self):
        manager = SessionManager()
        self.assertIsNone(manager.get_session("nonexistent"))

    def test_delete_session(self):
        manager = SessionManager()
        manager.create_session("sess_del")
        self.assertTrue(manager.delete_session("sess_del"))
        self.assertIsNone(manager.get_session("sess_del"))
        self.assertFalse(manager.delete_session("sess_del"))

    def test_add_message(self):
        manager = SessionManager()
        manager.create_session("sess_msg")
        
        msg = Message(
            sender="user", 
            text="hi", 
            timestamp=datetime.utcnow(), 
            message_id="m1"
        )
        updated = manager.add_message_to_session("sess_msg", msg)
        
        self.assertEqual(len(updated.messages), 1)
        self.assertEqual(updated.messages[0].message_id, "m1")
        
        # Add duplicate (should be ignored)
        manager.add_message_to_session("sess_msg", msg)
        self.assertEqual(len(updated.messages), 1)

    def test_add_message_no_session(self):
        manager = SessionManager()
        msg = Message(
            sender="user", 
            text="hi", 
            timestamp=datetime.utcnow(), 
            message_id="m1"
        )
        with self.assertRaises(ValueError):
            manager.add_message_to_session("missing", msg)

    def test_validate_history(self):
        manager = SessionManager()
        manager.create_session("sess_hist")
        
        msg1 = Message(sender="user", text="hi", timestamp=datetime.utcnow(), message_id="m1")
        msg2 = Message(sender="agent", text="hello", timestamp=datetime.utcnow(), message_id="m2")
        
        manager.add_message_to_session("sess_hist", msg1)
        
        self.assertTrue(manager.validate_history("sess_hist", [msg1]))
        self.assertTrue(manager.validate_history("sess_hist", []))
        
        # Mismatch content (ID check)
        msg3 = Message(sender="user", text="bad", timestamp=datetime.utcnow(), message_id="m3")
        self.assertFalse(manager.validate_history("sess_hist", [msg3]))
        
        # Append to stored
        manager.add_message_to_session("sess_hist", msg2)
        self.assertTrue(manager.validate_history("sess_hist", [msg1, msg2]))
        
        # Prefix
        self.assertTrue(manager.validate_history("sess_hist", [msg1]))
        
        # Too long
        msg4 = Message(sender="user", text="future", timestamp=datetime.utcnow(), message_id="m4")
        self.assertFalse(manager.validate_history("sess_hist", [msg1, msg2, msg4]))

    def test_cleanup_and_expiry(self):
        manager = SessionManager()
        # Mock settings by modifying instance directly for test
        manager._session_timeout = 0.5 
        
        manager.create_session("sess_exp")
        self.assertIsNotNone(manager.get_session("sess_exp"))
        
        time.sleep(0.6)
        
        # Should return None and expire
        self.assertIsNone(manager.get_session("sess_exp"))
        
        active = manager.list_active_sessions()
        self.assertNotIn("sess_exp", [s.session_id for s in active])

if __name__ == '__main__':
    unittest.main()

