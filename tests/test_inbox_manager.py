import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import inbox_manager

class TestInboxManager(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_inbox = Path(self.tmp_dir.name) / "state.json"
        self.patcher1 = patch.object(inbox_manager, "INBOX_FILE", str(self.tmp_inbox))
        self.patcher2 = patch.object(inbox_manager, "INBOX_DIR", str(self.tmp_dir.name))
        self.patcher1.start()
        self.patcher2.start()

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        self.tmp_dir.cleanup()

    def test_init_and_load_inbox(self):
        data = inbox_manager.load_inbox()
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["debate_turn_count"], 0)
        self.assertIsInstance(data["messages"], list)

    def test_add_message_and_debate_counter(self):
        inbox_manager.add_message("staff-backend", "frontend-architect", "Update schema")
        data = inbox_manager.load_inbox()
        self.assertEqual(len(data["messages"]), 1)
        self.assertEqual(data["debate_turn_count"], 1)
        self.assertIn("staff-backend", data["active_agents"])

    def test_debate_threshold_circuit_breaker(self):
        data = inbox_manager.load_inbox()
        data["debate_turn_count"] = 9
        inbox_manager.save_inbox(data)

        # 10th turn triggers circuit breaker auto-reset
        inbox_manager.add_message("staff-backend", "frontend-architect", "Another debate turn")
        reloaded = inbox_manager.load_inbox()
        self.assertEqual(reloaded["debate_turn_count"], 0)
        self.assertEqual(reloaded["status"], "active")

    def test_consensus_with_evidence(self):
        data = inbox_manager.load_inbox()
        data["messages"] = [
            {"sender": "staff-backend", "recipient": "qa", "content": "Evidence_Source: tests/test_api.py - verified"},
            {"sender": "qa", "recipient": "staff-backend", "content": "LGTM approved by QA Lead"}
        ]
        has_consensus = inbox_manager.check_consensus(data)
        self.assertTrue(has_consensus)
        self.assertEqual(data["status"], "consensus_reached")

    def test_consensus_rejected_without_evidence(self):
        data = inbox_manager.load_inbox()
        data["messages"] = [
            {"sender": "staff-backend", "recipient": "qa", "content": "LGTM looks fine"},
            {"sender": "qa", "recipient": "staff-backend", "content": "LGTM approved"}
        ]
        has_consensus = inbox_manager.check_consensus(data)
        self.assertFalse(has_consensus)

    def test_format_and_send_structured_message(self):
        msg = inbox_manager.format_structured_message(
            sender="staff-backend",
            recipient="qa-automation-lead",
            task="TASK-01-AUTH",
            status="IN_PROGRESS",
            verified=True,
            findings="Unit tests pass for JWT validation",
            files=["tests/test_auth.py", "auth.py"],
            decisions=["Use RS256 algorithm"],
            blockers="None",
            validation="python3 -m unittest tests/test_auth.py",
            next_action="Perform QA verification"
        )
        self.assertIn("FROM: staff-backend", msg)
        self.assertIn("TO: qa-automation-lead", msg)
        self.assertIn("VERIFIED: YES", msg)
        self.assertIn("TASK: TASK-01-AUTH", msg)

        sent = inbox_manager.send_structured_message(
            sender="staff-backend",
            recipient="qa-automation-lead",
            task="TASK-01-AUTH",
            status="DONE",
            verified=True,
            findings="Passed all tests",
            files=["auth.py"],
            decisions=["Approved"],
            blockers="None",
            validation="All gates green",
            next_action="Deploy"
        )
        self.assertTrue(sent)
        data = inbox_manager.load_inbox()
        self.assertEqual(len(data["messages"]), 1)
        self.assertIn("TASK: TASK-01-AUTH", data["messages"][0]["content"])


if __name__ == "__main__":
    unittest.main()
