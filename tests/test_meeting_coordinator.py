import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import meeting_coordinator

class TestMeetingCoordinator(unittest.TestCase):
    def test_preventive_action_detects_high_turns(self):
        data = {"debate_turn_count": 8, "status": "active"}
        with patch("subprocess.run") as mock_run:
            meeting_coordinator.handle_preventive_action(data)
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            self.assertIn("inbox_manager.py", args[1])
            self.assertIn("PREVENTIVE WARNING", args[-1])

    def test_corrective_action_unblocks_blocked_room(self):
        data = {"debate_turn_count": 12, "status": "blocked"}
        with patch.object(meeting_coordinator, "save_blackboard") as mock_save, \
             patch.object(meeting_coordinator, "run_scrum_master") as mock_scrum:
            meeting_coordinator.handle_corrective_action(data)
            self.assertEqual(data["status"], "active")
            self.assertEqual(data["debate_turn_count"], 0)
            mock_save.assert_called_once()
            mock_scrum.assert_called_once()

    def test_single_cycle_executes_report(self):
        with patch.object(meeting_coordinator, "load_blackboard", return_value=None), \
             patch("subprocess.run") as mock_run:
            meeting_coordinator.run_single_cycle()
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            self.assertIn("report", args)

if __name__ == "__main__":
    unittest.main()
