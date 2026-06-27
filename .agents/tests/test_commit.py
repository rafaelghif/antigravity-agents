import unittest
from unittest.mock import patch, mock_open
import sys
import os

# Inject CLI commands folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import commit

class TestCommitCommand(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data='{"profiles": [{"name": "test-prof", "email": "test@domain.com", "active": true}]}')
    @patch('os.path.exists')
    def test_load_profiles(self, mock_exists, mock_file):
        mock_exists.return_value = True
        data = commit.load_profiles()
        self.assertEqual(data["profiles"][0]["name"], "test-prof")

    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"profiles": [{"name": "corp-work", "email": "corp@work.com", "active": true}]}')
    def test_run_commit_swapping(self, mock_file, mock_exists, mock_sub):
        mock_exists.return_value = True
        # Mock successful git config, validation execution, and commit command
        mock_sub.return_value = unittest.mock.Mock(returncode=0)
        
        with patch('sys.exit') as mock_exit:
            commit.run(["-m", "feat: test message", "--no-verify"])
            mock_exit.assert_called_once_with(0)

if __name__ == '__main__':
    unittest.main()
