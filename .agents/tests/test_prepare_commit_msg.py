import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

# Inject scripts folders
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
import prepare_commit_msg

class TestPrepareCommitMsg(unittest.TestCase):

    @patch('subprocess.run')
    def test_get_branch_name_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="feat/issue-085\n")
        self.assertEqual(prepare_commit_msg.get_branch_name(), "feat/issue-085")

    @patch('subprocess.run')
    def test_get_branch_name_failure(self, mock_run):
        mock_run.side_effect = Exception("git error")
        self.assertEqual(prepare_commit_msg.get_branch_name(), "")

    @patch('prepare_commit_msg.get_branch_name', return_value="feat/issue-085")
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="feat(cli): initial commit\n\n# Please enter commit msg\n")
    def test_main_msg_injection(self, mock_file, mock_exists, mock_branch):
        with patch('sys.argv', ['prepare_commit_msg.py', 'commit_file.txt']):
            prepare_commit_msg.main()
            
            handle = mock_file()
            written_data = "".join(call[0][0] for call in handle.write.call_args_list)
            self.assertIn("Refs: issue-085", written_data)
            self.assertTrue(written_data.index("Refs: issue-085") < written_data.index("# Please enter commit msg"))

    @patch('prepare_commit_msg.get_branch_name', return_value="feat/issue-085")
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="feat(cli): initial commit Refs: issue-085\n")
    def test_main_skip_if_already_present(self, mock_file, mock_exists, mock_branch):
        with patch('sys.argv', ['prepare_commit_msg.py', 'commit_file.txt']):
            prepare_commit_msg.main()
            
            handle = mock_file()
            handle.write.assert_not_called()

if __name__ == '__main__':
    unittest.main()
