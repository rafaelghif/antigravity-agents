import unittest
from unittest.mock import patch
import os
import sys
import tempfile
import shutil

# Ensure the cli directory is in the import path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".agents", "scripts", "cli"))
import commands.issue as issue

class TestIssueCommand(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to act as .agents
        self.test_dir = tempfile.mkdtemp()
        self.patcher = patch('utils.get_agents_dir', return_value=self.test_dir)
        self.mock_get_agents_dir = self.patcher.start()
        
    def tearDown(self):
        self.patcher.stop()
        shutil.rmtree(self.test_dir)
        
    def test_create_and_list_issues(self):
        # 1. Create a couple of issues
        issue.run(["issue", "create", "Bug 1", "This is description 1"])
        issue.run(["issue", "create", "Bug 2", "This is description 2"])
        
        # Verify files were created
        issues_dir = os.path.join(self.test_dir, "issues")
        self.assertTrue(os.path.exists(os.path.join(issues_dir, "issue_001.md")))
        self.assertTrue(os.path.exists(os.path.join(issues_dir, "issue_002.md")))
        
        # Verify content
        with open(os.path.join(issues_dir, "issue_001.md"), 'r') as f:
            content = f.read()
            self.assertIn('title: "Bug 1"', content)
            self.assertIn('status: open', content)
            self.assertIn('This is description 1', content)
            
        # 2. Test list issues (run doesn't crash)
        with patch('sys.stdout.isatty', return_value=False):
            issue.run(["issue", "list"])
            
    def test_view_issue(self):
        issue.run(["issue", "create", "Bug to View", "Details..."])
        with patch('sys.stdout.isatty', return_value=False):
            # View it
            issue.run(["issue", "view", "1"])
            
    def test_close_issue(self):
        issue.run(["issue", "create", "Bug to Close", "Details..."])
        issue_file = os.path.join(self.test_dir, "issues", "issue_001.md")
        
        # Check initial status
        meta, _ = issue.parse_frontmatter(issue_file)
        self.assertEqual(meta.get("status"), "open")
        self.assertEqual(meta.get("closed_at"), "null")
        
        # Close it
        issue.run(["issue", "close", "1"])
        
        # Check closed status
        meta, _ = issue.parse_frontmatter(issue_file)
        self.assertEqual(meta.get("status"), "closed")
        self.assertNotEqual(meta.get("closed_at"), "null")

    @patch('subprocess.check_output')
    @patch('subprocess.run')
    def test_checkout_issue(self, mock_run, mock_check_output):
        # Setup git branch output
        mock_check_output.side_effect = [
            b"user",             # git config user.name
            b"  main\n"          # git branch
        ]
        
        # Create issue
        issue.run(["issue", "create", "Fix Login", "Login fails..."])
        
        # Mock memory file path
        memory_file = os.path.join(self.test_dir, "memory.md")
        with open(memory_file, 'w') as f:
            f.write("### Sprint Tasks Checklist\n- **Current Task Target**: Configure\n- **State Flag**: `COMPLETED`\n")
            
        with patch('utils.get_memory_file', return_value=memory_file):
            issue.run(["issue", "checkout", "1"])
            
        # Verify git checkout -b was run
        mock_run.assert_any_call(["git", "checkout", "-b", "issue-1-fix-login"])
        
        # Verify memory.md updated
        with open(memory_file, 'r') as f:
            content = f.read()
            self.assertIn("Resolve issue #1: Fix Login", content)
            self.assertIn("- **State Flag**: `IN_PROGRESS`", content)

    @patch('subprocess.check_output')
    @patch('subprocess.run')
    def test_merge_issue(self, mock_run, mock_check_output):
        # Current branch is issue-1-fix-login
        mock_check_output.side_effect = [
            b"issue-1-fix-login", # git rev-parse --abbrev-ref HEAD
        ]
        
        # Create issue
        issue.run(["issue", "create", "Fix Login", "Login fails..."])
        issue_file = os.path.join(self.test_dir, "issues", "issue_001.md")
        
        # Mock memory file
        memory_file = os.path.join(self.test_dir, "memory.md")
        with open(memory_file, 'w') as f:
            f.write("Active Pull Request Target: `main`\n### Sprint Tasks Checklist\n- [/] Resolve issue #1: Fix Login\n- **Current Task Target**: Resolve\n- **State Flag**: `IN_PROGRESS`\n")
            
        orig_exists = os.path.exists
        with patch('utils.get_memory_file', return_value=memory_file):
            # Patch validate.sh check to do nothing
            with patch('os.path.exists', side_effect=lambda path: False if "validate.sh" in path or "compile_bootstrap.py" in path else orig_exists(path)):
                issue.run(["issue", "merge", "1"])
                
        # Verify status is closed
        meta, _ = issue.parse_frontmatter(issue_file)
        self.assertEqual(meta.get("status"), "closed")
        
        # Verify git checkout main and git merge issue-1-fix-login were called
        mock_run.assert_any_call(["git", "checkout", "main"])
        mock_run.assert_any_call(["git", "merge", "issue-1-fix-login", "--no-ff", "-m", "merge branch 'issue-1-fix-login' into 'main'"])

if __name__ == '__main__':
    unittest.main()
