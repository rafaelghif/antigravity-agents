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

if __name__ == '__main__':
    unittest.main()
