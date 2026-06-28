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

    @patch('os.path.exists')
    @patch('os.getenv')
    def test_get_pat(self, mock_getenv, mock_exists):
        # Env token present
        mock_getenv.return_value = "dummy-token"
        mock_exists.return_value = False
        self.assertEqual(git_api.get_pat(), "dummy-token")

        # Env token missing, and no profiles file
        mock_getenv.return_value = None
        mock_exists.return_value = False
        self.assertIsNone(git_api.get_pat())

        # Env token missing, but active profile has token in profiles file
        mock_getenv.return_value = None
        mock_exists.side_effect = lambda p: p == ".agents/git_profiles.json"
        
        mock_json_content = json.dumps({
            "profiles": [
                {"name": "p1", "email": "p1@test.com", "active": True, "git_token": "profile-token"}
            ]
        })
        with patch('builtins.open', mock_open(read_data=mock_json_content)):
            self.assertEqual(git_api.get_pat(), "profile-token")

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
        expected_path = os.path.join(".agents/issues", "issue_99.md")
        mock_file.assert_called_with(expected_path, 'w', encoding='utf-8')
        mock_file().write.assert_called()

    @patch('os.path.exists', return_value=True)
    def test_sync_lessons_to_rules(self, mock_exists):
        import sync
        
        lessons_content = "## Lessons Learned\n- **[2026-06-27]** **Token Efficiency**: Always specify file read ranges\n"
        rules_content = "# Project Rules\n"
        
        written_data = {}
        
        def mock_open_impl(filename, mode='r', **kwargs):
            filename_str = str(filename)
            mock_file_handle = MagicMock()
            
            if 'r' in mode:
                if "lessons-learned.md" in filename_str:
                    mock_file_handle.read.return_value = lessons_content
                else:
                    mock_file_handle.read.return_value = rules_content
            elif 'w' in mode:
                def write_impl(data):
                    written_data[filename_str] = data
                mock_file_handle.write.side_effect = write_impl
                
            mock_file_handle.__enter__.return_value = mock_file_handle
            return mock_file_handle

        with patch('builtins.open', mock_open_impl):
            sync.sync_lessons_to_rules()
            
        rules_written_key = next((k for k in written_data if "rules.md" in k), None)
        self.assertIsNotNone(rules_written_key)
        self.assertIn("## 5. Synthesized Rules", written_data[rules_written_key])
        self.assertIn("Token Efficiency", written_data[rules_written_key])

    @patch('importlib.util.spec_from_file_location')
    @patch('importlib.util.module_from_spec')
    @patch('os.path.exists', return_value=True)
    def test_sync_command_run(self, mock_exists, mock_module_from_spec, mock_spec_from_file):
        import commands.sync as sync_cmd
        
        mock_spec = MagicMock()
        mock_spec_from_file.return_value = mock_spec
        
        mock_sync_module = MagicMock()
        mock_module_from_spec.return_value = mock_sync_module
        
        sync_cmd.run([])
        
        mock_sync_module.sync_skills_to_agents_md.assert_called_once()
        mock_sync_module.sync_adrs_to_architecture_md.assert_called_once()
        mock_sync_module.sync_lessons_to_rules.assert_called_once()

if __name__ == '__main__':
    unittest.main()
