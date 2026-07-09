import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
import json
import tempfile
import shutil

# Inject scripts folders
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli')))

import commands.message as message

class TestMessageCommand(unittest.TestCase):
    def setUp(self):
        # Create temporary message directory for isolated testing
        self.test_dir = tempfile.mkdtemp()
        self.old_messages_dir = message.MESSAGES_DIR
        message.MESSAGES_DIR = os.path.join(self.test_dir, "messages")
        
    def tearDown(self):
        message.MESSAGES_DIR = self.old_messages_dir
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('os.path.exists')
    @patch('builtins.open')
    @patch('subprocess.run')
    def test_get_sender_identity_from_profile(self, mock_sub, mock_file_open, mock_exists):
        # Profile config exists
        mock_exists.return_value = True
        mock_json_content = json.dumps({
            "profiles": [
                {"name": "Alice", "email": "alice@test.com", "active": True}
            ]
        })
        # Mock file open
        mock_file_open.return_value.__enter__.return_value.read.return_value = mock_json_content
        
        sender = message.get_sender_identity()
        self.assertEqual(sender, "Alice")

    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_get_sender_identity_fallback(self, mock_sub, mock_exists):
        # Profile config does not exist
        mock_exists.return_value = False
        
        mock_res = MagicMock()
        mock_res.stdout = "Bob\n"
        mock_sub.return_value = mock_res
        
        sender = message.get_sender_identity()
        self.assertEqual(sender, "Bob")

    @patch('commands.message.get_sender_identity')
    @patch('subprocess.run')
    def test_message_send(self, mock_sub, mock_sender):
        mock_sender.return_value = "Alice"
        mock_res = MagicMock()
        mock_res.stdout = "feat/issue-223\n"
        mock_sub.return_value = mock_res
        
        # Call send
        message.run(["send", "reviewer-agent", "request_review", '{"msg": "Please review"}'])
        
        # Verify message JSON file was created
        msg_dir = message.MESSAGES_DIR
        self.assertTrue(os.path.exists(msg_dir))
        files = os.listdir(msg_dir)
        self.assertEqual(len(files), 1)
        
        msg_file = os.path.join(msg_dir, files[0])
        with open(msg_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.assertEqual(data["sender"], "Alice")
        self.assertEqual(data["recipient"], "reviewer-agent")
        self.assertEqual(data["status"], "pending")
        self.assertEqual(data["payload"]["action"], "request_review")
        self.assertEqual(data["payload"]["msg"], "Please review")

    @patch('commands.message.get_sender_identity')
    def test_message_list_and_status(self, mock_sender):
        mock_sender.return_value = "Alice"
        
        # Send a message first
        message.run(["send", "reviewer-agent", "request_review", '{"msg": "Please review"}'])
        
        files = os.listdir(message.MESSAGES_DIR)
        msg_id = files[0].replace(".json", "")
        
        # Test updating status
        message.run(["status", msg_id, "completed", '{"status": "ok"}'])
        
        # Verify update
        msg_file = os.path.join(message.MESSAGES_DIR, files[0])
        with open(msg_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.assertEqual(data["status"], "completed")
        self.assertEqual(data["reply"]["status"], "ok")

if __name__ == '__main__':
    unittest.main()
