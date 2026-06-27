import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os

# Inject scripts folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
import validate

class TestValidate(unittest.TestCase):
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="node_modules/\n*.log\n# comment\n")
    def test_parse_antigravity_ignore(self, mock_file, mock_exists):
        mock_exists.return_value = True
        patterns = validate.parse_antigravity_ignore()
        self.assertEqual(len(patterns), 2)
        # Test matching
        self.assertTrue(validate.is_ignored_by_antigravity("src/node_modules/foo", patterns))
        self.assertTrue(validate.is_ignored_by_antigravity("error.log", patterns))
        self.assertFalse(validate.is_ignored_by_antigravity("src/main.py", patterns))

    @patch('subprocess.run')
    def test_is_git_ignored(self, mock_run):
        # Mock git check-ignore returns 0 (ignored)
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(validate.is_git_ignored("ignored_file.txt"))
        
        # Mock git check-ignore returns 1 (not ignored)
        mock_run.return_value = MagicMock(returncode=1)
        self.assertFalse(validate.is_git_ignored("normal_file.txt"))

    @patch('os.path.exists')
    def test_audit_critical_files(self, mock_exists):
        # All exist
        mock_exists.return_value = True
        self.assertTrue(validate.audit_critical_files())
        
        # Missing critical file
        mock_exists.side_effect = lambda path: "rules.md" not in path
        self.assertFalse(validate.audit_critical_files())

    @patch('os.path.exists')
    @patch('subprocess.run')
    @patch('validate.is_git_ignored')
    @patch('validate.is_ignored_by_antigravity')
    def test_audit_secrets_and_ignored_files_rejections(self, mock_anti, mock_git, mock_run, mock_exists):
        # Mock exists to return False for git_profiles.json
        mock_exists.side_effect = lambda path: False if 'git_profiles.json' in path else True
        
        # Mock git diff returning staged files
        mock_run.return_value = MagicMock(returncode=0, stdout="src/main.py\n")
        
        # Scenario 1: normal file
        mock_git.return_value = False
        mock_anti.return_value = False
        self.assertTrue(validate.audit_secrets_and_ignored_files())
        
        # Scenario 2: git ignored file staged
        mock_git.return_value = True
        mock_anti.return_value = False
        self.assertFalse(validate.audit_secrets_and_ignored_files())
        
        # Scenario 3: antigravity ignored file staged
        mock_git.return_value = False
        mock_anti.return_value = True
        self.assertFalse(validate.audit_secrets_and_ignored_files())

if __name__ == '__main__':
    unittest.main()
