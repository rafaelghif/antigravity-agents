import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os

# Inject CLI commands folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import dashboard

class TestDashboardCommand(unittest.TestCase):
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="---\nid: issue-126\ntitle: \"My Test Issue\"\nstatus: open\ngithub_number: 12\n---\n")
    def test_get_issue_frontmatter(self, mock_file, mock_exists):
        fm = dashboard.get_issue_frontmatter(".agents/issues/issue_126.md")
        self.assertEqual(fm.get("id"), "issue-126")
        self.assertEqual(fm.get("title"), "My Test Issue")
        self.assertEqual(fm.get("status"), "open")
        self.assertEqual(fm.get("github_number"), "12")

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('subprocess.run')
    @patch('validate.audit_critical_files', return_value=True)
    @patch('validate.audit_secrets_and_ignored_files', return_value=True)
    @patch('validate.audit_link_integrity', return_value=True)
    @patch('validate.audit_git_branch_alignment', return_value=True)
    @patch('validate.audit_workspace_sync', return_value=True)
    @patch('validate.audit_task_board_schema', return_value=True)
    @patch('validate.audit_static_linting', return_value=True)
    @patch('validate.audit_unit_tests', return_value=True)
    @patch('validate.audit_module_locks', return_value=True)
    @patch('validate.audit_commit_messages', return_value=True)
    def test_get_dashboard_data(self, mock_commit, mock_locks, mock_tests, mock_lint, mock_board, mock_sync, mock_git, mock_link, mock_sec, mock_crit, mock_sub, mock_file, mock_exists):
        # Configure subprocess for git branch
        mock_sub.return_value = MagicMock(returncode=0, stdout="feat/issue-126")
        
        mock_file.return_value.read.side_effect = [
            "- **Version:** 2.106.0", # AGENTS.md
            '{"app/models/user.py": {"branch": "feat/issue-126", "timestamp": "2026-07-02 21:00"}}', # locks.json
            "---\nid: issue-126\ntitle: \"Active Task\"\nstatus: open\n---\n- [ ] Subtask 1", # issue_126.md (get_issue_frontmatter)
            "---\nid: issue-126\ntitle: \"Active Task\"\nstatus: open\n---\n- [ ] Subtask 1", # issue_126.md (tasks extraction)
            "# Lessons\n## Lessons Learned\n- My Lesson", # lessons-learned.md
            "## 5. Synthesized Rules (Self-Learning Memory)\n- My Synthesized Rule", # rules.md
            "## [2.106.0] - 2026-07-02" # CHANGELOG.md
        ]
        
        data = dashboard.get_dashboard_data()
        
        self.assertEqual(data["version"], "2.106.0")
        self.assertEqual(len(data["locks"]), 1)
        self.assertEqual(data["locks"][0]["module"], "app/models/user.py")
        self.assertEqual(data["active_issue"]["id"], "ISSUE-126")
        self.assertEqual(data["active_issue"]["title"], "Active Task")
        self.assertIn("My Lesson", data["lessons"])
        self.assertIn("My Synthesized Rule", data["rules"])
        self.assertTrue(data["compliance"]["Critical Files"])

    @patch('subprocess.run')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('issue.sync_board_with_issues')
    def test_toggle_issue_task(self, mock_sync, mock_file_open, mock_exists, mock_sub):
        mock_sub.return_value = MagicMock(returncode=0, stdout="feat/issue-130\n")
        
        file_content = "---\nid: issue-130\ntitle: \"Modernize Dashboard\"\nstatus: open\n---\n- [ ] Subtask 1\n- [ ] Subtask 2"
        mock_file_open.return_value.read.return_value = file_content
        
        success = dashboard.toggle_issue_task(1, True)
        self.assertTrue(success)
        
        # Verify it wrote back the content with [x] for Subtask 2
        write_args = "".join(call.args[0] for call in mock_file_open.return_value.write.call_args_list)
        self.assertIn("- [x] Subtask 2", write_args)
        self.assertIn("- [ ] Subtask 1", write_args)
        mock_sync.assert_called_once()

if __name__ == '__main__':
    unittest.main()
