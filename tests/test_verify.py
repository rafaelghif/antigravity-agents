import sys
import unittest
import tempfile
import json
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from scripts import verify

class TestVerify(unittest.TestCase):
    def test_detect(self):
        checks = verify.detect()
        self.assertIsInstance(checks, list)
        self.assertTrue(len(checks) > 0)
        # Ensure each detected check has 3 components: name, stack, command
        for name, stack, cmd in checks:
            self.assertIsInstance(name, str)
            self.assertIsInstance(stack, str)
            self.assertIsInstance(cmd, str)

    @patch('sys.argv', ['verify.py', '--terse', '--execute'])
    @patch('subprocess.run')
    def test_main_execution(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "OK"
        mock_run.return_value.stderr = ""
        exit_code = verify.main()
        self.assertEqual(exit_code, 0)

    def test_handoff_bootstrapping(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            handoff_path = tmp_root / "handoff.json"
            self.assertFalse(handoff_path.exists())
            
            baseline = {
                "task_id": "INIT",
                "worker_role": "scrum-master",
                "summary": f"Initialized AAC workspace for {tmp_root.name}",
                "modifications": [],
                "tests": [],
                "confidence_score": 1.0,
                "requires_human": False
            }
            handoff_path.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
            self.assertTrue(handoff_path.is_file())
            
            loaded = json.loads(handoff_path.read_text(encoding="utf-8"))
            self.assertEqual(loaded["task_id"], "INIT")
            self.assertEqual(loaded["worker_role"], "scrum-master")

    @patch('sys.argv', ['verify.py', '--release'])
    def test_release_gate_missing_aitl(self):
        with patch.object(verify, 'ROOT', Path('/non/existent/path')):
            exit_code = verify.main()
            self.assertEqual(exit_code, 1)

    def test_split_cmd_posix(self):
        with patch('sys.platform', 'linux'):
            cmd = '/usr/bin/python3 scripts/verify.py --terse'
            parts = verify.split_cmd(cmd)
            self.assertEqual(parts, ['/usr/bin/python3', 'scripts/verify.py', '--terse'])

    def test_split_cmd_windows_preserves_backslashes(self):
        with patch('sys.platform', 'win32'):
            cmd = r'"C:\Program Files\Python311\python.exe" scripts\verify.py --terse'
            parts = verify.split_cmd(cmd)
            self.assertEqual(parts[0], r'C:\Program Files\Python311\python.exe')
            self.assertEqual(parts[1], r'scripts\verify.py')
            self.assertEqual(parts[2], '--terse')

    def test_detect_bun_and_packagemanager(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            (tmp_root / "package.json").write_text(json.dumps({
                "packageManager": "bun@1.1.0",
                "scripts": {"test": "bun test"}
            }))
            (tmp_root / "bun.lockb").write_text("")
            with patch.object(verify, 'ROOT', tmp_root):
                checks = verify.detect()
                self.assertTrue(any("bun run test" in cmd for _, _, cmd in checks))

    @patch('sys.argv', ['verify.py', '--terse'])
    def test_not_verified_when_no_checks(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_root = Path(tmpdir)
            with patch.object(verify, 'ROOT', empty_root):
                from io import StringIO
                captured = StringIO()
                with patch('sys.stdout', captured):
                    code = verify.main()
                self.assertEqual(code, 0)
                self.assertIn("NOT VERIFIED", captured.getvalue())

    @patch('sys.argv', ['verify.py', '--execute', '--terse'])
    def test_not_verified_when_checks_detected_but_tools_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir)
            (p / "Cargo.toml").write_text("[package]\nname = 'demo'\n")
            with patch.object(verify, 'ROOT', p):
                with patch('shutil.which', return_value=None):
                    from io import StringIO
                    captured = StringIO()
                    with patch('sys.stdout', captured):
                        code = verify.main()
                    self.assertEqual(code, 1)
                    output = captured.getvalue()
                    self.assertIn("NOT VERIFIED", output)
                    self.assertNotIn("OK", output)

    def test_verify_with_target_path_argument(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir)
            (p / "go.mod").write_text("module demo\ngo 1.21\n")
            with patch('sys.argv', ['verify.py', str(p), '--terse']):
                from io import StringIO
                captured = StringIO()
                with patch('sys.stdout', captured):
                    code = verify.main()
                self.assertEqual(code, 0)
                self.assertIn("DRY-RUN", captured.getvalue())

if __name__ == '__main__':
    unittest.main()

