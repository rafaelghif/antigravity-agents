import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
import json

# Inject scripts folders
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli')))
import git_api
import commands.issue as issue

class TestSync(unittest.TestCase):

    @patch('os.getenv')
    def test_get_pat(self, mock_getenv):
        # Env token present
        mock_getenv.return_value = "dummy-token"
        self.assertEqual(git_api.get_pat(), "dummy-token")

        # Env token missing
        mock_getenv.return_value = None
        self.assertIsNone(git_api.get_pat())

    @patch('git_api.get_pat')
    @patch('git_api.get_repo_info')
    @patch('urllib.request.urlopen')
    def test_fetch_github_issues_success(self, mock_urlopen, mock_repo, mock_pat):
        mock_pat.return_value = "token"
        mock_repo.return_value = "owner/repo"
        
        # Mock API response
        mock_res = MagicMock()
        mock_res.read.return_value = b'[{"number": 42, "title": "Test Issue", "state": "open", "html_url": "url"}]'
        mock_urlopen.return_value.__enter__.return_value = mock_res
        
        res = git_api.fetch_github_issues()
        self.assertIsNotNone(res)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["number"], 42)

    @patch('os.makedirs')
    @patch('git_api.fetch_github_issues')
    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_sync_issues_creates_file(self, mock_file, mock_listdir, mock_exists, mock_fetch, mock_makedirs):
        # Remote returns one new issue
        mock_fetch.return_value = [{"number": 99, "title": "New Issue", "state": "open", "html_url": "url-99", "body": "description"}]
        mock_exists.return_value = False  # Dir and file don't exist
        mock_listdir.return_value = []
        
        issue.sync_issues()
        
        # Verify it tries to create issue_99.md
        mock_file.assert_called_with(".agents/issues/issue_99.md", 'w', encoding='utf-8')
        mock_file().write.assert_called()

if __name__ == '__main__':
    unittest.main()
