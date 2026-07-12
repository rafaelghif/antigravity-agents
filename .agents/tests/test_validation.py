import unittest
import os
import sys

# Inject CLI commands folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import validation

class TestInputValidation(unittest.TestCase):
    
    def test_validate_safe_path(self):
        # Valid paths
        self.assertTrue(validation.validate_safe_path("~/.ssh/id_rsa"))
        self.assertTrue(validation.validate_safe_path("C:\\Users\\User\\.ssh\\id_rsa"))
        self.assertTrue(validation.validate_safe_path("path/with spaces/key.txt"))
        self.assertTrue(validation.validate_safe_path("relative/path-to/file_1.md"))
        
        # Invalid/dangerous paths
        self.assertFalse(validation.validate_safe_path("~/.ssh/id_rsa; touch /tmp/pwned"))
        self.assertFalse(validation.validate_safe_path("~/.ssh/id_rsa&&rm -rf /"))
        self.assertFalse(validation.validate_safe_path("~/.ssh/id_rsa|some_command"))
        self.assertFalse(validation.validate_safe_path("~/.ssh/id_rsa`whoami`"))
        self.assertFalse(validation.validate_safe_path("~/.ssh/id_rsa$(whoami)"))
        self.assertFalse(validation.validate_safe_path(None))
        self.assertFalse(validation.validate_safe_path(""))

    def test_validate_safe_identifier(self):
        # Valid identifiers
        self.assertTrue(validation.validate_safe_identifier("my-profile-123"))
        self.assertTrue(validation.validate_safe_identifier("issue_330"))
        self.assertTrue(validation.validate_safe_identifier("task-harden-core"))
        self.assertTrue(validation.validate_safe_identifier("validate.py"))
        
        # Invalid/dangerous identifiers
        self.assertFalse(validation.validate_safe_identifier("my profile;"))
        self.assertFalse(validation.validate_safe_identifier("issue-123&rm"))
        self.assertFalse(validation.validate_safe_identifier("task-123|whoami"))
        self.assertFalse(validation.validate_safe_identifier("`whoami`"))
        self.assertFalse(validation.validate_safe_identifier("$(whoami)"))
        self.assertFalse(validation.validate_safe_identifier(None))
        self.assertFalse(validation.validate_safe_identifier(""))

    def test_validate_safe_branch(self):
        # Valid branch names
        self.assertTrue(validation.validate_safe_branch("feat/issue-330"))
        self.assertTrue(validation.validate_safe_branch("fix/harden-core"))
        self.assertTrue(validation.validate_safe_branch("main"))
        self.assertTrue(validation.validate_safe_branch("task_123"))
        
        # Invalid/dangerous branch names
        self.assertFalse(validation.validate_safe_branch("feat/issue-330;whoami"))
        self.assertFalse(validation.validate_safe_branch("feat/issue-330&&rm"))
        self.assertFalse(validation.validate_safe_branch("feat/issue-330|whoami"))
        self.assertFalse(validation.validate_safe_branch("`whoami`"))
        self.assertFalse(validation.validate_safe_branch("$(whoami)"))
        self.assertFalse(validation.validate_safe_branch(None))
        self.assertFalse(validation.validate_safe_branch(""))

if __name__ == '__main__':
    unittest.main()
