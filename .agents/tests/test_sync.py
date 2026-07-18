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
                {"name": "p1", "email": "p1@test.com", "active": True, "git_pat": "profile-token"}
            ]
        })
        with patch('builtins.open', mock_open(read_data=mock_json_content)):
            self.assertEqual(git_api.get_pat(), "profile-token")

    @patch('git_api.get_service_info')
    @patch('urllib.request.urlopen')
    def test_fetch_github_issues_success(self, mock_urlopen, mock_service_info):
        mock_service_info.return_value = ("github", "https://api.github.com", "token", "owner", "repo")
        
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

    @patch('os.makedirs')
    @patch('git_api.fetch_github_issues')
    @patch('os.path.exists')
    @patch('os.listdir')
    def test_sync_issues_updates_mismatched_status(self, mock_listdir, mock_exists, mock_fetch, mock_makedirs):
        # Existing local issue has status: open
        # We also put status: open in the description body to ensure it is not touched
        mock_exists.return_value = True
        mock_listdir.return_value = ["issue_42.md"]
        mock_fetch.return_value = [{"number": 42, "title": "Test Issue", "state": "closed", "html_url": "url"}]

        local_content = """---
id: issue-42
title: "Test Issue"
status: open
assignee: agent-antigravity
created_at: 2026-07-02
github_url: "url"
github_number: 42
---

# Issue Details
Problem status: open
"""

        mock_file_handle = mock_open(read_data=local_content)
        with patch('builtins.open', mock_file_handle):
            issue.sync_issues()

            # Inspect the calls to write
            handle = mock_file_handle()
            written_data = "".join(call[0][0] for call in handle.write.call_args_list)
            # Frontmatter status should be updated to closed
            self.assertIn("status: closed", written_data)
            # Body status should still be open
            self.assertIn("Problem status: open", written_data)

    @patch('git_api.fetch_github_issues', return_value=None)
    @patch('commands.services.issue_service.sync_board_with_issues')
    def test_sync_issues_offline_mode(self, mock_sync_board, mock_fetch):
        # When remote_issues is None, it should skip execution cleanly
        issue.sync_issues()
        mock_sync_board.assert_called_once()

    @patch('os.path.exists', return_value=True)
    def test_sync_lessons_to_rules(self, mock_exists):
        old_path = sys.path[:]
        sys.path = [p for p in sys.path if not p.endswith('commands')]
        if 'sync' in sys.modules:
            del sys.modules['sync']
        try:
            import sync
        finally:
            sys.path = old_path
        
        lessons_content = """lessons:
  - date: "2026-07-02"
    category: "Testing / Mocking"
    content: "Ensure mock side effects are isolated"
  - date: "2026-06-27"
    category: "Python Mock Leaks"
    content: "When mocking sys.exit in Python"
  - date: "2026-07-01"
    category: "OS Compatibility / PowerShell"
    content: "Use cross-platform path helpers"
  - date: "2026-06-30"
    category: "Git & Security"
    content: "Validate GPG keys"
  - date: "2026-06-29"
    category: "Performance"
    content: "Optimize validators"
  - date: "2026-06-28"
    category: "Workspace Optimization"
    content: "Specify read ranges"
  - date: "2026-06-25"
    category: "Dummy Category"
    content: "This is a test dummy rule"
"""
        rules_content = "# Project Rules\n"
        
        written_data = {}
        
        import io
        def mock_open_impl(filename, mode='r', **kwargs):
            filename_str = str(filename)
            mock_file_handle = MagicMock()
            
            if 'r' in mode:
                if "lessons-learned.yaml" in filename_str:
                    mock_file_handle = io.StringIO(lessons_content)
                elif "lessons-archive.yaml" in filename_str:
                    mock_file_handle = io.StringIO("")
                else:
                    mock_file_handle = io.StringIO(rules_content)
                    
                # We also need to mock __enter__ for StringIO to work in a context manager
                mock_file_handle.__enter__ = lambda self: self
                mock_file_handle.__exit__ = lambda self, exc_type, exc_val, exc_tb: None
            elif 'w' in mode:
                def write_impl(data):
                    if filename_str not in written_data:
                        written_data[filename_str] = ""
                    written_data[filename_str] += data
                mock_file_handle.write.side_effect = write_impl
                mock_file_handle.__enter__.return_value = mock_file_handle
                
            return mock_file_handle

        with patch('builtins.open', side_effect=mock_open_impl):
            sync.sync_lessons_to_rules()
            
        rules_written_key = next((k for k in written_data if "rules.md" in k), None)
        archive_written_key = next((k for k in written_data if "lessons-archive.yaml" in k), None)
        
        self.assertIsNotNone(rules_written_key)
        self.assertIn("## 6. Synthesized Rules", written_data[rules_written_key])
        
        # Testing / Mocking and Python Mock Leaks should be clustered together
        self.assertIn("Testing / Mocking", written_data[rules_written_key])
        self.assertIn("Ensure mock side effects are isolated; When mocking sys.exit in Python", written_data[rules_written_key])
        
        # Git & Security, Performance, and Workspace Optimization should be included in rules.md
        self.assertIn("Git & Security", written_data[rules_written_key])
        self.assertIn("Performance", written_data[rules_written_key])
        self.assertIn("Workspace Optimization", written_data[rules_written_key])
        
        # Dummy Category should be archived since we cap at 5 canonical rules
        self.assertIsNotNone(archive_written_key)
        self.assertIn("Dummy Category", written_data[archive_written_key])
        self.assertNotIn("Dummy Category", written_data[rules_written_key])

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
