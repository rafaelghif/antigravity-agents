import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os

# Inject CLI commands folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import issue
import learn

class TestIssueCommand(unittest.TestCase):
    @patch('os.listdir')
    @patch('os.path.exists')
    def test_get_issue_path(self, mock_exists, mock_listdir):
        mock_exists.return_value = True
        mock_listdir.return_value = ["issue_028.md", "issue_029.md"]
        
        path = issue.get_issue_path("issue-028")
        self.assertEqual(path, os.path.join(issue.ISSUE_DIR, "issue_028.md"))
        
        path_normalized = issue.get_issue_path("issue_029")
        self.assertEqual(path_normalized, os.path.join(issue.ISSUE_DIR, "issue_029.md"))

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="## Todo\n\n## Doing\n- [ ] Task title (feat/issue-123) <!-- id: issue-123 -->\n\n## Done\n")
    def test_update_board_completed(self, mock_file, mock_exists):
        mock_exists.return_value = True
        
        # Test board transition
        with patch('builtins.open', mock_file):
            issue.update_board_completed("issue-123")
            
            # Retrieve mock write arguments
            handle = mock_file()
            written_data = "".join(call[0][0] for call in handle.write.call_args_list)
            self.assertIn("## Done\n- [x] Task title (feat/issue-123) <!-- id: issue-123 -->", written_data)
            self.assertNotIn("## Doing\n- [ ] Task title (feat/issue-123)", written_data)

    @patch('learn.suggest_and_record_lessons')
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="---\nid: issue-029\nstatus: open\ngithub_number: 12\n---\n")
    def test_issue_close_flow(self, mock_file, mock_exists, mock_sub, mock_suggest):
        # Setup mocks
        mock_exists.side_effect = lambda p: True
        
        def mock_run_side_effect(cmd, *args, **kwargs):
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
            if "rev-parse" in cmd_str:
                return MagicMock(returncode=0, stdout="feat/issue-029\n")
            elif "show-ref" in cmd_str:
                if "feat/issue-029" in cmd_str:
                    return MagicMock(returncode=0)
                elif "master" in cmd_str:
                    return MagicMock(returncode=1) # master does not exist, main is base
                return MagicMock(returncode=0)
            return MagicMock(returncode=0, stdout="")
        
        mock_sub.side_effect = mock_run_side_effect
        
        with patch('issue.update_board_completed') as mock_board:
            with patch('git_api.close_github_issue') as mock_git_api:
                mock_git_api.return_value = True
                
                # Run the close action
                issue.run(["close", "issue-029"])
                
                # Verify board was updated and remote github issue was closed
                mock_board.assert_called_once_with("issue-029")
                mock_git_api.assert_called_once_with(12)
                mock_suggest.assert_called_once()
                
                # Check that correct file writes occurred
                handle = mock_file()
                written_data = "".join(call[0][0] for call in handle.write.call_args_list)
                self.assertIn("status: closed", written_data)

    @patch('git_api.get_pat', return_value="dummy-pat")
    @patch('git_api.get_repo_info', return_value="owner/repo")
    @patch('git_api.create_github_issue', return_value=("https://github.com/owner/repo/issues/123", 123))
    @patch('os.path.exists', return_value=True)
    @patch('os.listdir', return_value=["issue_100.md"])
    @patch('builtins.open', new_callable=mock_open, read_data="---\nid: issue-100\ntitle: \"Offline issue\"\n---\n")
    def test_push_offline_issues_success(self, mock_file, mock_listdir, mock_exists, mock_create, mock_repo, mock_pat):
        issue.push_offline_issues()
        mock_create.assert_called_once_with("Offline issue", "Local tracking ID: issue-100")
        handle = mock_file()
        written_data = "".join(call[0][0] for call in handle.write.call_args_list)
        self.assertIn("github_url: \"https://github.com/owner/repo/issues/123\"", written_data)
        self.assertIn("github_number: 123", written_data)

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_sync_board_with_issues(self, mock_file, mock_listdir, mock_exists):
        # Setup mocks
        mock_exists.side_effect = lambda p: True
        mock_listdir.side_effect = lambda d: ["issue_126.md"] if ("issues" in d and "archive" not in d) else []
        
        # Mock file contents: issue frontmatter and board.md
        issue_content = "---\nid: issue-126\ntitle: \"My Test Issue\"\nstatus: closed\n---\n"
        board_content = "# Board\n## Todo\n- [ ] My Test Issue (feat/issue-126) <!-- id: issue-126 -->\n## Doing\n## Done\n"
        
        # Configure file reading mock
        mock_file.return_value.read.side_effect = [issue_content, board_content]
        
        issue.sync_board_with_issues()
        
        # Verify that it updated the file and moved issue-126 to Done [x]
        handle = mock_file()
        written_data = "".join(call[0][0] for call in handle.write.call_args_list)
        self.assertIn("- [x] My Test Issue", written_data)

import git_api

class TestGitApiCaching(unittest.TestCase):
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"last_sync_time": 1000.0, "cached_issues": [{"id": 1, "title": "Cached"}]}')
    @patch('time.time', return_value=1050.0)
    @patch('git_api.get_pat', return_value="dummy-pat")
    @patch('git_api.get_repo_info', return_value="owner/repo")
    @patch('urllib.request.urlopen')
    def test_fetch_github_issues_cached(self, mock_urlopen, mock_repo, mock_pat, mock_time, mock_file, mock_exists):
        mock_exists.return_value = True
        res = git_api.fetch_github_issues()
        self.assertEqual(res, [{"id": 1, "title": "Cached"}])
        mock_urlopen.assert_not_called()

    @patch('os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open)
    @patch('time.time', return_value=1000.0)
    @patch('git_api.get_pat', return_value="dummy-pat")
    @patch('git_api.get_repo_info', return_value="owner/repo")
    @patch('urllib.request.urlopen')
    def test_fetch_github_issues_uncached(self, mock_urlopen, mock_repo, mock_pat, mock_time, mock_file, mock_exists):
        mock_res = MagicMock()
        mock_res.read.return_value = b'[{"id": 2, "title": "Fresh"}]'
        mock_urlopen.return_value.__enter__.return_value = mock_res
        
        res = git_api.fetch_github_issues()
        self.assertEqual(res, [{"id": 2, "title": "Fresh"}])
        mock_urlopen.assert_called_once()
        mock_file().write.assert_called()



if __name__ == '__main__':
    unittest.main()
