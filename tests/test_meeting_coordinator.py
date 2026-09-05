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

    def test_run_agent_passes_high_effort_flags(self):
        with patch("shutil.which", return_value="/usr/local/bin/agy"), \
             patch("subprocess.run") as mock_run:
            meeting_coordinator.run_agent("scrum-master", "Plan sprint")
            agy_calls = [call for call in mock_run.call_args_list if call[0][0][0] == "agy"]
            self.assertTrue(len(agy_calls) > 0)
            cmd = agy_calls[0][0][0]
            self.assertIn("--model", cmd)
            self.assertIn("gemini-3.8-flash-high", cmd)
            self.assertIn("--effort", cmd)
            self.assertIn("high", cmd)

            meeting_coordinator.run_agent("staff-backend", "Write architecture")
            agy_calls2 = [call for call in mock_run.call_args_list if call[0][0][0] == "agy"]
            cmd2 = agy_calls2[-1][0][0]
            self.assertIn("--model", cmd2)
            self.assertIn("gemini-3.1-pro-high", cmd2)
            self.assertIn("--effort", cmd2)
            self.assertIn("high", cmd2)

if __name__ == "__main__":
    unittest.main()
