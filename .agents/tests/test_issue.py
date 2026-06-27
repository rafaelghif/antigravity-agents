import unittest
from unittest.mock import patch, mock_open
import sys
import os

# Inject CLI commands folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import issue

class TestIssueCommand(unittest.TestCase):
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('os.listdir')
    def test_get_issue_path(self, mock_listdir, mock_makedirs, mock_exists):
        mock_exists.return_value = False
        mock_listdir.return_value = []
        path = issue.get_issue_path("issue-123")
        self.assertTrue(path.endswith("issue_123.md"))

    @patch('builtins.open', new_callable=mock_open, read_data="status: open\n")
    @patch('os.path.exists')
    def test_close_issue(self, mock_exists, mock_file):
        mock_exists.return_value = True
        with patch('issue.get_issue_path') as mock_path:
            mock_path.return_value = "dummy_path.md"
            issue.run(["close", "issue-123"])
            mock_file().write.assert_called_once()
            self.assertIn("status: closed", mock_file().write.call_args[0][0])

if __name__ == '__main__':
    unittest.main()
