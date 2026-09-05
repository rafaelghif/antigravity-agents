import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import auto_reviewer

class TestAutoReviewer(unittest.TestCase):
    def test_format_review_approved(self):
        body, event = auto_reviewer.format_review(0, "All gates green", "", "2 files changed")
        self.assertEqual(event, "APPROVE")
        self.assertIn("APPROVED", body)
        self.assertIn("2 files changed", body)

    def test_format_review_request_changes(self):
        body, event = auto_reviewer.format_review(1, "", "AST complexity exceeded", "1 file changed")
        self.assertEqual(event, "REQUEST_CHANGES")
        self.assertIn("REQUEST CHANGES", body)
        self.assertIn("AST complexity exceeded", body)

    def test_get_git_repo_parses_origin(self):
        with patch.object(auto_reviewer, "run_cmd", return_value=(0, "https://github.com/test-org/test-repo.git\n", "")):
            repo = auto_reviewer.get_git_repo()
            self.assertEqual(repo, "test-org/test-repo")

    def test_get_git_repo_empty_when_no_origin(self):
        with patch.object(auto_reviewer, "run_cmd", return_value=(1, "", "fatal: no remote")):
            repo = auto_reviewer.get_git_repo()
            self.assertEqual(repo, "")

if __name__ == "__main__":
    unittest.main()
