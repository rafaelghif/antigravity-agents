import unittest
import sys
import os

# Inject parent directory containing scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from core.entities import GitProfile, ModuleLock, TokenBudget, Issue, ValidationError

class TestEntities(unittest.TestCase):

    def test_git_profile_success(self) -> None:
        p = GitProfile(
            name="corporate-work",
            email="developer@company.com",
            signing_key="ssh-ed25519 AAAAC3NzaC1l",
            ssh_key_path="~/.ssh/id_ed25519_corp",
            git_pat="encrypted:abc",
            active=True
        )
        p.validate()
        self.assertEqual(p.name, "corporate-work")
        self.assertEqual(p.email, "developer@company.com")
        self.assertTrue(p.active)

        # Test to/from dict roundtrip
        d = p.to_dict()
        self.assertEqual(d["name"], "corporate-work")
        self.assertEqual(d["email"], "developer@company.com")
        self.assertEqual(d["signing_key"], "ssh-ed25519 AAAAC3NzaC1l")
        self.assertEqual(d["ssh_key_path"], "~/.ssh/id_ed25519_corp")
        
        p2 = GitProfile.from_dict(d)
        p2.validate()
        self.assertEqual(p2.name, p.name)
        self.assertEqual(p2.email, p.email)

    def test_git_profile_validation_failures(self) -> None:
        # Empty name
        with self.assertRaises(ValidationError) as ctx:
            GitProfile(name="", email="dev@corp.com").validate()
        self.assertIn("Profile name cannot be empty", str(ctx.exception))

        # Invalid name characters
        with self.assertRaises(ValidationError) as ctx:
            GitProfile(name="bad name", email="dev@corp.com").validate()
        self.assertIn("Invalid profile name format", str(ctx.exception))

        # Invalid email format
        with self.assertRaises(ValidationError) as ctx:
            GitProfile(name="dev", email="not_an_email").validate()
        self.assertIn("Invalid email format", str(ctx.exception))

        # Command injection check on ssh_key_path
        with self.assertRaises(ValidationError) as ctx:
            GitProfile(name="dev", email="dev@corp.com", ssh_key_path="~/.ssh/key; rm -rf").validate()
        self.assertIn("Command injection detected in ssh_key_path", str(ctx.exception))

        # Command injection check on gitea_host
        with self.assertRaises(ValidationError) as ctx:
            GitProfile(name="dev", email="dev@corp.com", gitea_host="https://gitea.com;ls").validate()
        self.assertIn("Command injection/space characters detected", str(ctx.exception))

        # Invalid gitea host protocol
        with self.assertRaises(ValidationError) as ctx:
            GitProfile(name="dev", email="dev@corp.com", gitea_host="ftp://gitea.com").validate()
        self.assertIn("Gitea host must start with http:// or https://", str(ctx.exception))

    def test_module_lock_success(self) -> None:
        lock = ModuleLock(module="src/validate.py", branch="feat/issue-123")
        lock.validate()
        self.assertEqual(lock.module, "src/validate.py")
        self.assertEqual(lock.branch, "feat/issue-123")

    def test_module_lock_validation_failures(self) -> None:
        # Command injection on module path
        with self.assertRaises(ValidationError):
            ModuleLock(module="src/validate.py; rm -rf", branch="feat/issue-123").validate()

        # Command injection on branch name
        with self.assertRaises(ValidationError):
            ModuleLock(module="src/validate.py", branch="feat/issue-123 && evil").validate()

        # Empty branch
        with self.assertRaises(ValidationError):
            ModuleLock(module="src/validate.py", branch="").validate()

    def test_token_budget_success(self) -> None:
        budget = TokenBudget(
            account="user@gmail.com",
            daily_limit=1000,
            daily_used=100,
            monthly_limit=10000,
            monthly_used=1500
        )
        budget.validate()
        self.assertEqual(budget.daily_limit, 1000)
        self.assertEqual(budget.monthly_used, 1500)
        
        # Test dict roundtrip
        d = budget.to_dict()
        budget2 = TokenBudget.from_dict("user@gmail.com", d)
        budget2.validate()
        self.assertEqual(budget2.daily_limit, 1000)

    def test_token_budget_validation_failures(self) -> None:
        # Negative limit
        with self.assertRaises(ValidationError):
            TokenBudget(account="test", daily_limit=-5).validate()
            
        with self.assertRaises(ValidationError):
            TokenBudget(account="test", monthly_used=-100).validate()

    def test_issue_success(self) -> None:
        issue = Issue(
            id="issue-345",
            title="feat: Implement initial models",
            status="doing",
            assignee="rafaelghif",
            created_at="2026-07-16",
            github_url="https://github.com/org/repo/issues/345",
            github_number=345
        )
        issue.validate()
        self.assertEqual(issue.id, "issue-345")
        self.assertEqual(issue.status, "doing")
        self.assertEqual(issue.github_number, 345)

        # Test to/from dict roundtrip
        d = issue.to_dict()
        self.assertEqual(d["github_number"], 345)
        issue2 = Issue.from_dict(d)
        issue2.validate()
        self.assertEqual(issue2.title, issue.title)

    def test_issue_validation_failures(self) -> None:
        # Invalid status
        with self.assertRaises(ValidationError) as ctx:
            Issue(id="issue-1", title="title", status="not_a_status").validate()
        self.assertIn("Invalid status value", str(ctx.exception))

        # Invalid issue ID format
        with self.assertRaises(ValidationError) as ctx:
            Issue(id="issue 1", title="title").validate()
        self.assertIn("Invalid Issue ID format", str(ctx.exception))
        
        # Empty ID
        with self.assertRaises(ValidationError):
            Issue(id="", title="title").validate()

if __name__ == '__main__':
    unittest.main()
