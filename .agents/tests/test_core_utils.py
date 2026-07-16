import unittest
import io
import os
import sys
import json
import subprocess
from unittest.mock import patch

# Inject parent directory containing scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from core.logger import StructuredLogger, LogLevel
from core.executor import ShellExecutor, ExecutionResult

class TestLogger(unittest.TestCase):

    @patch('sys.stdout.isatty', return_value=False)
    def test_logger_colors_disabled_by_default_in_non_tty(self, mock_isatty) -> None:
        # Mock sys.stdout.isatty to ensure it behaves deterministically in non-tty mode
        logger = StructuredLogger("TEST")
        self.assertFalse(logger.color_enabled)

    def test_logger_format_plain(self) -> None:
        logger = StructuredLogger("TEST")
        logger.color_enabled = False
        logger.json_format = False
        
        msg = logger._format_message(LogLevel.INFO, "hello")
        self.assertEqual(msg, "[INFO] hello")

        msg_err = logger._format_message(LogLevel.ERROR, "fail")
        self.assertEqual(msg_err, "[FAIL] fail")

    def test_logger_format_json(self) -> None:
        logger = StructuredLogger("TEST")
        logger.json_format = True
        
        msg = logger._format_message(LogLevel.WARN, "warning", {"key": "val"})
        data = json.loads(msg)
        self.assertEqual(data["level"], "WARN")
        self.assertEqual(data["message"], "warning")
        self.assertEqual(data["key"], "val")
        self.assertEqual(data["logger"], "TEST")

    def test_logger_outputs(self) -> None:
        logger = StructuredLogger("TEST")
        logger.color_enabled = False
        logger.json_format = False
        
        # Capture stdout
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            logger.info("info message")
        self.assertEqual(captured.getvalue().strip(), "[INFO] info message")

class TestExecutor(unittest.TestCase):

    def test_executor_success(self) -> None:
        executor = ShellExecutor()
        res = executor.execute([sys.executable, "-c", "print('hello')"])
        self.assertTrue(res.success)
        self.assertEqual(res.stdout.strip(), "hello")
        self.assertGreater(res.duration, 0.0)

    def test_executor_failure(self) -> None:
        executor = ShellExecutor()
        res = executor.execute([sys.executable, "-c", "raise SystemExit(42)"])
        self.assertFalse(res.success)
        self.assertEqual(res.returncode, 42)

    def test_executor_check_raises_error(self) -> None:
        executor = ShellExecutor()
        with self.assertRaises(subprocess.CalledProcessError):
            executor.execute([sys.executable, "-c", "raise SystemExit(1)"], check=True)

    def test_executor_sanitization(self) -> None:
        executor = ShellExecutor()
        
        # Verify blacklisted characters raise ValueError
        unsafe_cmds = [
            ["echo", "hello; rm -rf /"],
            ["echo", "hello && evil"],
            ["echo", "hello || evil"],
            ["echo", "hello | evil"],
            ["echo", "hello `evil`"],
            ["echo", "hello $(evil)"],
            ["echo", "hello\nevil"]
        ]
        
        for cmd in unsafe_cmds:
            with self.assertRaises(ValueError) as ctx:
                executor.execute(cmd)
            self.assertIn("Unsafe shell argument blocked", str(ctx.exception))

    def test_executor_bypass_sanitization(self) -> None:
        # If sanitization is disabled, it should not raise error
        executor = ShellExecutor(sanitize=False)
        res = executor.execute(["echo", "hello; echo world"])
        self.assertTrue(res.success)

if __name__ == '__main__':
    unittest.main()
