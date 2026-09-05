import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import autonomous_loop

class TestAutonomousLoop(unittest.TestCase):
    def test_find_pending_tasks(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tasks_dir = Path(tmp_dir)
            (tasks_dir / "01_done.yaml").write_text('id: 1\nstatus: "DONE"\n', encoding="utf-8")
            (tasks_dir / "02_pending.yaml").write_text('id: 2\nstatus: "IN_PROGRESS"\n', encoding="utf-8")
            (tasks_dir / "03_not_started.yaml").write_text('id: 3\ntitle: "Pending"\n', encoding="utf-8")

            pending = autonomous_loop.find_pending_tasks(tasks_dir)
            self.assertIn("02_pending.yaml", pending)
            self.assertIn("03_not_started.yaml", pending)
            self.assertNotIn("01_done.yaml", pending)

    def test_orchestrate_task_blackboard_fallback(self):
        with patch("shutil.which", return_value=None), \
             patch("subprocess.run") as mock_run:
            success = autonomous_loop.orchestrate_task("test_task.yaml", ROOT)
            self.assertTrue(success)
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            self.assertIn("inbox_manager.py", args[1])

    def test_orchestrate_task_passes_high_effort_flags(self):
        with patch("shutil.which", return_value="/usr/local/bin/agy"), \
             patch("subprocess.run") as mock_run:
            success = autonomous_loop.orchestrate_task("test_task.yaml", ROOT)
            self.assertTrue(success)
            # Find the agy call
            agy_calls = [call for call in mock_run.call_args_list if call[0][0][0] == "agy"]
            self.assertTrue(len(agy_calls) > 0)
            called_cmd = agy_calls[0][0][0]
            self.assertIn("--model", called_cmd)
            self.assertIn("gemini-3.8-flash-high", called_cmd)
            self.assertIn("--effort", called_cmd)
            self.assertIn("high", called_cmd)

    def test_run_loop_idle_when_no_tasks(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            exit_code = autonomous_loop.run_loop(Path(tmp_dir))
            self.assertEqual(exit_code, 0)

if __name__ == "__main__":
    unittest.main()
