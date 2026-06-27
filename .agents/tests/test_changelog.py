import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os

# Inject scripts folders
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli')))
import commands.changelog as changelog

class TestChangelog(unittest.TestCase):

    def test_bump_semver(self):
        # Case 1: Breaking change -> Major bump
        categories = {
            "breaking": ["API changes"],
            "feat": [], "fix": []
        }
        self.assertEqual(changelog.bump_semver("1.2.3", categories), "2.0.0")

        # Case 2: Feat change -> Minor bump
        categories = {
            "breaking": [],
            "feat": ["Add user login"],
            "fix": [], "refactor": [], "docs": [], "chore": [], "test": [], "other": []
        }
        self.assertEqual(changelog.bump_semver("1.2.3", categories), "1.3.0")

        # Case 3: Fix change -> Patch bump
        categories = {
            "breaking": [], "feat": [],
            "fix": ["Resolve crash"], "refactor": [], "docs": [], "chore": [], "test": [], "other": []
        }
        self.assertEqual(changelog.bump_semver("1.2.3", categories), "1.2.4")

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="- **Product:** AAC\n- **Version:** 2.1.0\n")
    def test_get_current_version(self, mock_file, mock_exists):
        mock_exists.return_value = True
        self.assertEqual(changelog.get_current_version(), "2.1.0")

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="# Changelog\n\n## [2.1.0] - 2026-06-27\n")
    def test_get_latest_changelog_version(self, mock_file, mock_exists):
        mock_exists.return_value = True
        self.assertEqual(changelog.get_latest_changelog_version(), "2.1.0")

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('builtins.open', new_callable=mock_open, read_data="# Issue 022: Auto-Changelog Feature\n")
    def test_extract_issue_title(self, mock_file, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = ["issue_022.md"]
        title = changelog.extract_issue_title("issue-022")
        self.assertEqual(title, "Auto-Changelog Feature")

    @patch('commands.changelog.extract_issue_title')
    def test_parse_conventional_commits(self, mock_extract):
        mock_extract.return_value = "Auto-Changelog Feature"
        commits = [
            ("hash1", "feat(scope): add parser (issue-022)"),
            ("hash2", "fix: fix minor issue"),
            ("hash3", "chore: tidy up files")
        ]
        categories = changelog.parse_conventional_commits(commits)
        self.assertEqual(categories["feat"], ["Auto-Changelog Feature (ISSUE-022)"])
        self.assertEqual(categories["fix"], ["fix minor issue"])
        self.assertEqual(categories["chore"], ["tidy up files"])

if __name__ == '__main__':
    unittest.main()
