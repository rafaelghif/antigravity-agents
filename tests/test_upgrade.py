import unittest
import os
import sys
from pathlib import Path

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.upgrade import parse_semver, is_newer_version

class TestUpgrade(unittest.TestCase):
    def test_parse_semver(self):
        self.assertEqual(parse_semver("v4.18.0"), (4, 18, 0))
        self.assertEqual(parse_semver("4.18.0"), (4, 18, 0))
        self.assertEqual(parse_semver("v5.0.0-rc1"), (5, 0, 0))
        self.assertEqual(parse_semver("latest"), (0, 0, 0))

    def test_is_newer_version(self):
        self.assertTrue(is_newer_version("v4.19.0", "4.18.0"))
        self.assertTrue(is_newer_version("v5.0.0", "v4.18.0"))
        self.assertFalse(is_newer_version("v4.18.0", "4.18.0"))
        self.assertFalse(is_newer_version("v4.17.0", "4.18.0"))

    def test_install_aac_with_local_source_override(self):
        import tempfile
        from install import install_aac
        with tempfile.TemporaryDirectory() as target_dir, tempfile.TemporaryDirectory() as src_dir:
            target_path = Path(target_dir)
            src_path = Path(src_dir)
            
            # Setup mock minimal source structure
            (src_path / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
            (src_path / "GEMINI.md").write_text("# Workspace Bootstrap\nAGENTS.md\n", encoding="utf-8")
            (src_path / ".agents" / "brain").mkdir(parents=True)
            (src_path / ".agents" / "config.json").write_text('{"core_version": "4.44.3"}', encoding="utf-8")
            (src_path / "scripts").mkdir(parents=True)
            
            # Run installation with source_override
            success = install_aac(target_path, "v4.44.3", source_override=src_path)
            self.assertTrue(success)
            self.assertTrue((target_path / "AGENTS.md").is_file())
            self.assertTrue((target_path / "GEMINI.md").is_file())
            
            # Verify .gitignore contains both scratch and backup directories
            gi_path = target_path / ".gitignore"
            self.assertTrue(gi_path.is_file())
            gi_content = gi_path.read_text(encoding="utf-8")
            self.assertIn(".agents/scratch/", gi_content)
            self.assertIn(".agents-backups/", gi_content)


    def test_upgrade_upstream_fallback_uses_temporary_file(self):
        import io
        import urllib.request
        from unittest.mock import patch, MagicMock
        from scripts import upgrade

        mock_script = "import sys\nprint('upgraded')\nsys.exit(0)\n"
        mock_resp = MagicMock()
        mock_resp.read.return_value = mock_script.encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp

        executed_cmd = []

        def fake_run(cmd, **kwargs):
            executed_cmd.extend(cmd)
            res = MagicMock()
            res.returncode = 0
            return res

        with patch("pathlib.Path.is_file", return_value=False), \
             patch("urllib.request.urlopen", return_value=mock_resp), \
             patch("subprocess.run", side_effect=fake_run), \
             patch("sys.exit") as mock_exit:
            upgrade.main()
            mock_exit.assert_called_with(0)

        # Check that executed command used a .py script path, not -c
        self.assertGreater(len(executed_cmd), 1)
        self.assertEqual(executed_cmd[0], sys.executable)
        self.assertTrue(executed_cmd[1].endswith(".py"), f"Expected .py file, got {executed_cmd[1]}")
        self.assertNotEqual(executed_cmd[1], "-c")


if __name__ == '__main__':
    unittest.main()
