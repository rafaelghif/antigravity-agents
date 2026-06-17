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
        def side_effect(args, **kwargs):
            if "config" in args:
                return b"user"
            elif "branch" in args:
                return b"  main\n"
            elif "remote" in args:
                return b"https://github.com/owner/repo.git"
            return b""
        mock_check_output.side_effect = side_effect

        
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
        def side_effect(args, **kwargs):
            if "rev-parse" in args:
                return b"issue-1-fix-login"
            elif "remote" in args:
                return b"https://github.com/owner/repo.git"
            elif "config" in args:
                return b"Agent"
            return b""
        mock_check_output.side_effect = side_effect

        
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

    @patch('subprocess.check_output')
    def test_provider_detection(self, mock_check_output):
        # Test GitHub detection
        mock_check_output.return_value = b"https://github.com/owner/repo.git\n"
        res = issue.get_provider_and_repo()
        self.assertEqual(res, ("github", "https://api.github.com", "owner", "repo"))
        
        # Test GitLab detection
        mock_check_output.return_value = b"git@gitlab.com:owner/repo.git\n"
        res = issue.get_provider_and_repo()
        self.assertEqual(res, ("gitlab", "https://gitlab.com", "owner", "repo"))
        
        # Test Gitea detection
        mock_check_output.return_value = b"http://localhost:3000/owner/repo.git\n"
        res = issue.get_provider_and_repo()
        self.assertEqual(res, ("gitea", "http://localhost:3000", "owner", "repo"))

    @patch('subprocess.check_output')
    def test_active_profile_token_resolution(self, mock_check_output):
        mock_check_output.return_value = b"work@company.com\n"
        profiles_file = os.path.join(self.test_dir, 'git_profiles')
        with open(profiles_file, 'w', encoding='utf-8') as f:
            f.write("work.email=work@company.com\nwork.github_token=gh_val\nwork.gitlab_token=gl_val\nwork.gitea_token=gt_val\nwork.gitea_url=http://127.0.0.1:3000\n")
            
        token, url = issue.get_active_profile_token("github")
        self.assertEqual(token, "gh_val")
        self.assertIsNone(url)
        
        token, url = issue.get_active_profile_token("gitlab")
        self.assertEqual(token, "gl_val")
        self.assertIsNone(url)
        
        token, url = issue.get_active_profile_token("gitea")
        self.assertEqual(token, "gt_val")
        self.assertEqual(url, "http://127.0.0.1:3000")

if __name__ == '__main__':
    unittest.main()
