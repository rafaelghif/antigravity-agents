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

if __name__ == '__main__':
    unittest.main()
