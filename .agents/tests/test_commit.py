import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

# Inject CLI commands folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import commit

class TestCommitCommand(unittest.TestCase):
    def test_has_user_defined_profiles(self):
        placeholders = [
            {"name": "corporate-work", "email": "developer@company.com", "active": True},
            {"name": "personal-github", "email": "dev.personal@gmail.com", "active": False}
        ]
        self.assertFalse(commit.has_user_defined_profiles(placeholders))
        
        user_defined = [
            {"name": "corporate-work", "email": "developer@company.com", "active": False},
            {"name": "custom", "email": "rafaelghifari@company.com", "active": True}
        ]
        self.assertTrue(commit.has_user_defined_profiles(user_defined))

    @patch('subprocess.run')
    @patch('commit.load_profiles')
    def test_commit_fallback_behavior(self, mock_load_profiles, mock_run):
        # Setup example profiles structure (placeholders only)
        mock_load_profiles.return_value = {
            "profiles": [
                {"name": "corporate-work", "email": "developer@company.com", "active": True},
                {"name": "personal-github", "email": "dev.personal@gmail.com", "active": False}
            ]
        }
        
        # Scenario 1: Local email is already configured, profiles are unconfigured placeholders.
        # It should NOT call git config to overwrite.
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="user@custom.com\n"), # git config user.email check
            MagicMock(returncode=0, stdout="User Name\n"),      # git config user.name check
            MagicMock(returncode=0)                            # validator check/run
        ]
        
        with patch('sys.exit') as mock_exit:
            commit.run(["--no-verify"])
            
            # Verify that git config was NOT called with developer@company.com
            call_args_strs = [" ".join(call[0][0]) for call in mock_run.call_args_list]
            self.assertFalse(any("developer@company.com" in cmd for cmd in call_args_strs))

        # Scenario 2: Local email is empty. It SHOULD apply corporate-work profile.
        mock_run.reset_mock()
        mock_run.side_effect = [
            MagicMock(returncode=1, stdout=""), # git config user.email is empty/failed
            MagicMock(returncode=1, stdout=""), # git config user.name is empty/failed
            MagicMock(returncode=0),            # git config user.email local write
            MagicMock(returncode=0),            # git config user.name local write
            MagicMock(returncode=0),            # git config gpg unsets
            MagicMock(returncode=0),
            MagicMock(returncode=0)             # git commit execution
        ]
        
        with patch('sys.exit') as mock_exit:
            commit.run(["--no-verify"])
            
            # Verify that git config WAS called with developer@company.com
            call_args_strs = [" ".join(call[0][0]) for call in mock_run.call_args_list]
            self.assertTrue(any("developer@company.com" in cmd for cmd in call_args_strs))

if __name__ == '__main__':
    unittest.main()
