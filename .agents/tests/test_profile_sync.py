import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
import json

# Inject scripts folders
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli')))
import validate

class TestProfileSync(unittest.TestCase):

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"profiles": [{"name": "p1", "email": "p1@corp.com", "active": false}, {"name": "p2", "email": "p2@corp.com", "active": true}]}')
    @patch('subprocess.run')
    def test_validate_profile_auto_sync(self, mock_run, mock_file, mock_exists):
        mock_exists.return_value = True
        
        # Current Git email is p1@corp.com (registered but inactive)
        def mock_git_calls(args, **kwargs):
            if 'diff' in args:
                return MagicMock(returncode=0, stdout="")
            elif 'config' in args:
                return MagicMock(returncode=0, stdout="p1@corp.com\n")
            return MagicMock(returncode=0)
            
        mock_run.side_effect = mock_git_calls
        
        # Verify that validation succeeds and updates profile active states
        self.assertTrue(validate.audit_secrets_and_ignored_files())
        
        # Open write mode check
        mock_file.assert_any_call(".agents/git_profiles.json", 'w', encoding='utf-8')

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"profiles": [{"name": "p1", "email": "p1@corp.com", "active": true}]}')
    @patch('subprocess.run')
    def test_validate_profile_unregistered_blocks(self, mock_run, mock_file, mock_exists):
        mock_exists.return_value = True
        
        # Current Git email is wrong@personal.com (unregistered)
        def mock_git_calls(args, **kwargs):
            if 'diff' in args:
                return MagicMock(returncode=0, stdout="")
            elif 'config' in args:
                return MagicMock(returncode=0, stdout="wrong@personal.com\n")
            return MagicMock(returncode=0)
            
        mock_run.side_effect = mock_git_calls
        
        # Verify that validation fails
        self.assertFalse(validate.audit_secrets_and_ignored_files())

if __name__ == '__main__':
    unittest.main()
