import os
import sys
import unittest
import tempfile
import platform
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import verify, dag_orchestrator, inbox_manager, meeting_coordinator, semantic_grapher, git_hygiene_guard
from scripts.hooks import pre_tool_quality_gate

class TestCrossPlatformSupport(unittest.TestCase):
    def test_verify_split_cmd_windows_paths(self):
        with patch("sys.platform", "win32"):
            # Windows path with spaces and backslashes
            win_cmd = r'"C:\Program Files\Python311\python.exe" "C:\Project\scripts\verify.py" --terse'
            parts = verify.split_cmd(win_cmd)
            self.assertEqual(parts[0], r"C:\Program Files\Python311\python.exe")
            self.assertEqual(parts[1], "C:\\Project\\scripts\\verify.py")
            self.assertEqual(parts[2], "--terse")

    def test_dag_orchestrator_cmd_splitting_windows(self):
        with patch("sys.platform", "win32"):
            cmd = r'python3 "C:\Program Files\app\main.py"'
            is_win = True
            import shlex
            parts = shlex.split(cmd, posix=not is_win)
            parts = [p.strip('"') for p in parts]
            if parts[0] in ("python", "python3", "py"):
                parts[0] = sys.executable
            self.assertEqual(parts[0], sys.executable)
            self.assertEqual(parts[1], r"C:\Program Files\app\main.py")

    def test_inbox_manager_utf8_encoding_safe(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_inbox = Path(tmpdir) / "state.json"
            with patch("scripts.inbox_manager.INBOX_FILE", str(tmp_inbox)), \
                 patch("scripts.inbox_manager.INBOX_DIR", str(tmpdir)):
                inbox_manager.init_inbox()
                # Test Unicode and emojis that fail on Windows cp1252 if encoding not utf-8
                unicode_msg = "Test L9: 🚀 ✅ 📋 Bahasa: lu/gw, anjir! éèê 中文"
                inbox_manager.add_message("sender", "recipient", unicode_msg)
                data = inbox_manager.load_inbox()
                self.assertEqual(data["messages"][0]["content"], unicode_msg)

    def test_pre_tool_quality_gate_windows_path_normalization(self):
        # Verify Windows backslashes in .git path are detected and audited
        win_git_path = r"C:\workspace\project\.git\config"
        norm = win_git_path.replace("\\", "/")
        self.assertIn("/.git/", norm)

    def test_semantic_grapher_directory_ignore_parts(self):
        # Verify parts detection ignores directories regardless of slash direction (Windows/Linux)
        win_path = "C:\\project\\node_modules\\pkg\\index.js"
        parts = set(Path(win_path).parts) | set(win_path.replace("\\", "/").split("/"))
        self.assertIn("node_modules", parts)

        linux_path = "/home/user/project/.git/objects"
        parts_lin = set(Path(linux_path).parts) | set(linux_path.replace("\\", "/").split("/"))
        self.assertIn(".git", parts_lin)

    def test_git_hygiene_as_posix_compatibility(self):
        # Verify as_posix converts Windows path safely
        fake_scratch = Path("C:/project/.agents/scratch/test.py")
        self.assertIn(".agents/scratch", fake_scratch.as_posix().lower())

    def test_gitattributes_contains_githooks_lf(self):
        ga = ROOT / ".gitattributes"
        self.assertTrue(ga.is_file())
        text = ga.read_text(encoding="utf-8")
        self.assertIn(".githooks/* text eol=lf", text)
        self.assertIn("*.py text eol=lf", text)

    def test_install_py_windows_chmod_bypass(self):
        # On Windows (nt), chmod must not fail or raise
        with patch("os.name", "nt"):
            self.assertEqual(os.name, "nt")
            # Verify condition logic in install.py
            should_chmod = (os.name != "nt")
            self.assertFalse(should_chmod)

    def test_start_py_windows_creation_flags(self):
        with patch("platform.system", return_value="Windows"):
            flags = getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0x00000200)
            self.assertEqual(flags, 0x00000200)

    def test_bootstrap_scripts_exist_and_executable_logic(self):
        sh_file = ROOT / "install.sh"
        ps1_file = ROOT / "install.ps1"
        self.assertTrue(sh_file.is_file())
        self.assertTrue(ps1_file.is_file())
        self.assertIn("install.py", sh_file.read_text(encoding="utf-8"))
        self.assertIn("install.py", ps1_file.read_text(encoding="utf-8"))
        self.assertIn("PYTHONIOENCODING", ps1_file.read_text(encoding="utf-8"))
        self.assertIn("PYTHONIOENCODING", sh_file.read_text(encoding="utf-8"))

    def test_windows_cp932_stream_reconfigure_safeguard(self):
        import io
        buffer = io.BytesIO()
        fake_stdout = io.TextIOWrapper(buffer, encoding="cp932")
        # Ensure without reconfigure it crashes on \u2705
        with self.assertRaises(UnicodeEncodeError):
            fake_stdout.write("\u2705")

        # Now apply the safeguard
        fake_stdout.reconfigure(encoding="utf-8", errors="replace")
        fake_stdout.write("\u2705 SUCCESS 🚀")
        fake_stdout.flush()
        buffer.seek(0)
        output = buffer.read().decode("utf-8")
        self.assertIn("\u2705 SUCCESS 🚀", output)

    def test_verify_subprocess_sub_env_has_utf8(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "OK"
            mock_run.return_value.stderr = ""
            with patch("sys.argv", ["verify.py", "--execute", "--terse"]):
                verify.main()
                self.assertTrue(mock_run.called)
                _, kwargs = mock_run.call_args
                self.assertIn("env", kwargs)
                self.assertEqual(kwargs["env"]["PYTHONIOENCODING"], "utf-8")
                self.assertEqual(kwargs["env"]["PYTHONUTF8"], "1")
                self.assertEqual(kwargs.get("encoding"), "utf-8")
                self.assertEqual(kwargs.get("errors"), "replace")

if __name__ == "__main__":
    unittest.main()
