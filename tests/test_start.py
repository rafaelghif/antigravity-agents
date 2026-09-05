import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import start

class TestStart(unittest.TestCase):
    def test_stop_process_terminates_and_closes_log(self):
        mock_proc = MagicMock(spec=subprocess.Popen)
        mock_log = MagicMock()
        
        start.stop_process(mock_proc, mock_log)
        
        mock_proc.terminate.assert_called_once()
        mock_proc.wait.assert_called_once()
        mock_log.close.assert_called_once()

    def test_stop_process_kills_on_timeout(self):
        mock_proc = MagicMock(spec=subprocess.Popen)
        mock_proc.wait.side_effect = [subprocess.TimeoutExpired(cmd="test", timeout=5), None]
        mock_log = MagicMock()
        
        start.stop_process(mock_proc, mock_log)
        
        mock_proc.terminate.assert_called_once()
        mock_proc.kill.assert_called_once()
        mock_log.close.assert_called_once()

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    @patch("time.sleep")
    def test_start_loop_happy_path(self, mock_sleep, mock_run, mock_popen):
        mock_proc = MagicMock()
        mock_proc.pid = 1234
        mock_popen.return_value = mock_proc
        mock_run.return_value.returncode = 0
        
        exit_code = start.start_loop()
        self.assertEqual(exit_code, 0)
        mock_proc.terminate.assert_called_once()

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    @patch("time.sleep")
    def test_start_loop_hermes_mode(self, mock_sleep, mock_run, mock_popen):
        mock_proc = MagicMock()
        mock_proc.pid = 5678
        mock_popen.return_value = mock_proc
        mock_run.return_value.returncode = 0
        
        exit_code = start.start_loop(mode="hermes")
        self.assertEqual(exit_code, 0)
        mock_proc.terminate.assert_called_once()
        # Verify hermes was launched
        called_cmd = mock_run.call_args[0][0]
        self.assertIn("hermes_manager.py", str(called_cmd))

if __name__ == "__main__":
    unittest.main()
