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

    @patch('commands.message.get_sender_identity')
    @patch('subprocess.run')
    def test_message_handover(self, mock_sub, mock_sender):
        mock_sender.return_value = "Alice"
        
        # Mock subprocess calls for git commands:
        # 1. git rev-parse (active branch name) -> feat/issue-226
        # 2. git status (for changes check) ->  M src/main.py
        # 3. git add -A
        # 4. git commit (handover message)
        # 5. git add (message file)
        # 6. git commit (add mailbox message)
        # 7. git push
        mock_run_res = MagicMock()
        mock_run_res.stdout = "feat/issue-226\n"
        mock_sub.return_value = mock_run_res
        
        message.run(["handover", "reviewer-agent", "review", '{"task": "verify"}'])
        
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
        self.assertEqual(data["payload"]["action"], "review")
        self.assertEqual(data["payload"]["task_id"], "issue-226")
        self.assertEqual(data["payload"]["task"], "verify")

    @patch('subprocess.run')
    def test_message_process_scaffold(self, mock_sub):
        # Create a pending message file manually in test dir
        msg_id = "msg_test123"
        msg = {
            "message_id": msg_id,
            "sender": "Alice",
            "recipient": "reviewer-agent",
            "status": "pending",
            "payload": {
                "task_id": "issue-226",
                "action": "scaffold"
            }
        }
        os.makedirs(message.MESSAGES_DIR, exist_ok=True)
        msg_file = os.path.join(message.MESSAGES_DIR, f"{msg_id}.json")
        with open(msg_file, 'w', encoding='utf-8') as f:
            json.dump(msg, f)
            
        mock_sub.return_value = MagicMock(returncode=0)
        
        message.run(["process", msg_id])
        
        # Verify status became completed
        with open(msg_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(data["status"], "completed")
        
        # Verify scaffold file was written
        scaffold_file = ".agents/plans/scaffold_result.md"
        self.assertTrue(os.path.exists(scaffold_file))
        # clean it up
        os.remove(scaffold_file)

    @patch('commands.message.get_sender_identity')
    @patch('subprocess.run')
    def test_message_receive_filters_and_processes(self, mock_sub, mock_sender):
        mock_sender.return_value = "reviewer-agent"
        
        # Create two pending messages, one for reviewer-agent, one for coder-agent
        msg_dir = message.MESSAGES_DIR
        os.makedirs(msg_dir, exist_ok=True)
        
        # Message 1 (for reviewer-agent)
        msg1 = {
            "message_id": "msg_1",
            "recipient": "reviewer-agent",
            "status": "pending",
            "payload": {"task_id": "issue-226", "action": "review"}
        }
        with open(os.path.join(msg_dir, "msg_1.json"), 'w', encoding='utf-8') as f:
            json.dump(msg1, f)
            
        # Message 2 (for coder-agent)
        msg2 = {
            "message_id": "msg_2",
            "recipient": "coder-agent",
            "status": "pending",
            "payload": {"task_id": "issue-226", "action": "scaffold"}
        }
        with open(os.path.join(msg_dir, "msg_2.json"), 'w', encoding='utf-8') as f:
            json.dump(msg2, f)
            
        mock_sub.return_value = MagicMock(returncode=0)
        
        message.run(["receive"])
        
        # msg_1 should be completed (processed because recipient matches active_sender_identity)
        with open(os.path.join(msg_dir, "msg_1.json"), 'r', encoding='utf-8') as f:
            data1 = json.load(f)
        self.assertEqual(data1["status"], "completed")
        
        # msg_2 should still be pending
        with open(os.path.join(msg_dir, "msg_2.json"), 'r', encoding='utf-8') as f:
            data2 = json.load(f)
        self.assertEqual(data2["status"], "pending")

if __name__ == '__main__':
    unittest.main()
