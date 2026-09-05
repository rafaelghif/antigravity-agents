import sys
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from scripts import validate

class TestValidate(unittest.TestCase):
    @patch('scripts.validate.validate_manifest')
    @patch('scripts.validate.validate_mcp')
    @patch('scripts.validate.validate_markdown_metadata')
    @patch('scripts.validate.validate_instruction_budget')
    @patch('scripts.validate.validate_settings')
    @patch('scripts.validate.validate_compatibility')
    @patch('scripts.validate.validate_recovery_state')
    @patch('scripts.validate.validate_scanner_applicability')
    @patch('scripts.validate.validate_version')
    @patch('scripts.validate.load_json')
    def test_main(self, *mocks):
        self.assertEqual(validate.main(), 0)

    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.read_text')
    def test_is_framework_repo(self, mock_read, mock_is_file):
        # In this repo, install.sh exists with antigravity-agents.git
        mock_is_file.return_value = True
        mock_read.return_value = "antigravity-agents.git"
        self.assertTrue(validate.is_framework_repo())

    def test_consumer_mode_manifest(self):
        # Consumer required paths should be a subset of framework paths
        for path in validate.CONSUMER_REQUIRED_PATHS:
            self.assertIn(path, validate.REQUIRED_PATHS)

    def test_optional_paths_excludes_soul(self):
        for path in validate.OPTIONAL_PATHS:
            self.assertNotIn("soul.md", path)

    def test_all_manifest_paths_exclude_soul(self):
        all_manifest_paths = (
            validate.OPTIONAL_PATHS
            + validate.REQUIRED_PATHS
            + validate.CONSUMER_REQUIRED_PATHS
            + validate.CORE_AGENT_PATHS
        )
        for path in all_manifest_paths:
            self.assertNotIn("soul.md", path)

    def test_install_brain_preserve_files_excludes_soul(self):
        import install
        self.assertNotIn("soul.md", install.BRAIN_PRESERVE_FILES)

if __name__ == '__main__':
    unittest.main()

