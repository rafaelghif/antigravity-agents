import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
import io

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
        self.assertEqual(categories["feat"], ["**scope:** Auto-Changelog Feature (ISSUE-022)"])
        self.assertEqual(categories["fix"], ["fix minor issue"])
        self.assertEqual(categories["chore"], ["tidy up files"])

    @patch('commands.changelog.get_current_version')
    @patch('commands.changelog.get_latest_changelog_version')
    @patch('commands.changelog.get_boundary_commit')
    @patch('commands.changelog.get_commits_since')
    @patch('commands.changelog.parse_conventional_commits')
    @patch('commands.changelog.bump_semver')
    @patch('commands.changelog.update_version_in_files')
    @patch('commands.changelog.update_changelog')
    @patch('git_api.create_github_release')
    def test_changelog_run_creates_github_release(self, mock_create_rel, mock_upd_changelog, mock_upd_files, mock_bump, mock_parse, mock_commits, mock_boundary, mock_latest, mock_curr):
        mock_curr.return_value = "1.0.0"
        mock_latest.return_value = "1.0.0"
        mock_boundary.return_value = "hash1"
        mock_commits.return_value = [("hash2", "feat: add feature")]
        mock_parse.return_value = {"feat": ["add feature"], "breaking": [], "fix": [], "refactor": [], "docs": [], "chore": [], "test": [], "other": []}
        mock_bump.return_value = "1.1.0"
        mock_upd_changelog.return_value = "## [1.1.0] - 2026-06-27\n### 🚀 Features\n- add feature\n"
        mock_create_rel.return_value = "https://github.com/test/repo/releases/tag/v1.1.0"
        
        changelog.run([])
        
        mock_upd_changelog.assert_called_once()
        mock_create_rel.assert_called_once_with(
            tag_name="v1.1.0",
            name="Release v1.1.0",
            body="### 🚀 Features\n- add feature",
            draft=True
        )

        mock_upd_changelog.assert_called_once()
        mock_create_rel.assert_called_once_with(
            tag_name="v1.1.0",
            name="Release v1.1.0",
            body="### 🚀 Features\n- add feature",
            draft=True
        )

    @patch('commands.changelog.extract_issue_title')
    def test_parse_conventional_commits_prioritization(self, mock_extract):
        mock_extract.return_value = "Auto-Changelog Feature"
        # Verify breaking change priority
        commits = [
            ("hash1", "fix: fix issue (issue-022)"),
            ("hash2", "feat!: breaking change (issue-022)"),
            ("hash3", "feat: normal feature (issue-022)")
        ]
        categories = changelog.parse_conventional_commits(commits)
        self.assertEqual(categories["breaking"], ["Auto-Changelog Feature (ISSUE-022)"])
        self.assertEqual(len(categories["feat"]), 0)
        self.assertEqual(len(categories["fix"]), 0)

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('builtins.open', new_callable=mock_open, read_data="---\ntitle: \"Bug fix description\"\n---\n")
    def test_classify_from_local_issue(self, mock_file, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = ["issue_022.md"]
        cat = changelog.classify_from_local_issue("issue-022")
        self.assertEqual(cat, "fix")

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('builtins.open', new_callable=mock_open, read_data="---\ntitle: \"Resolve versioning bug in installer\"\n---\n")
    def test_parse_commits_explicit_override_prevents_hallucination(self, mock_file, mock_listdir, mock_exists):
        mock_exists.return_value = True
        mock_listdir.return_value = ["issue_022.md"]
        
        # The commit message uses 'feat:'. It must NOT be overridden by the issue's bug fix category!
        commits = [("hash123", "feat: implement test features (Refs: issue-022)")]
        categories = changelog.parse_conventional_commits(commits)
        
        self.assertEqual(len(categories["feat"]), 1)
        self.assertEqual(len(categories["fix"]), 0)
        self.assertIn("Resolve versioning bug in installer", categories["feat"][0])

    @patch('subprocess.run')
    def test_get_boundary_commit_tags(self, mock_run):
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_res.stdout = "tag_commit_hash\n"
        mock_run.return_value = mock_res
        
        commit = changelog.get_boundary_commit("2.28.0")
        self.assertEqual(commit, "tag_commit_hash")

    @patch('commands.changelog.is_agent_core_repo')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('json.dump')
    def test_update_version_in_files_non_agent_repo(self, mock_json_dump, mock_json_load, mock_open_file, mock_exists, mock_is_agent):
        mock_is_agent.return_value = False
        
        # We mock exists such that package.json exists, but bootstrap.py does not.
        def exists_side_effect(path):
            if path == "package.json":
                return True
            if path == "AGENTS.md":
                return True
            return False
        mock_exists.side_effect = exists_side_effect
        mock_json_load.return_value = {"name": "test-project", "version": "1.0.0"}
        
        changelog.update_version_in_files("1.0.0", "1.1.0")
        
        # Verify that json.dump was called to update version to 1.1.0
        mock_json_dump.assert_called_once()
        args, kwargs = mock_json_dump.call_args
        self.assertEqual(args[0]["version"], "1.1.0")

    @patch('git_api.get_repo_info')
    @patch('os.path.exists')
    def test_is_agent_core_repo(self, mock_exists, mock_repo_info):
        # Case 1: git_api returns antigravity-agents remote url
        mock_repo_info.return_value = "rafaelghif/antigravity-agents"
        mock_exists.return_value = False
        self.assertTrue(changelog.is_agent_core_repo())

        # Case 2: git_api does not return it (and AGENTS.md product is ignored)
        mock_repo_info.return_value = None
        mock_exists.return_value = True
        with patch('builtins.open', new_callable=mock_open, read_data="- **Product:** test-proj\n"):
            self.assertFalse(changelog.is_agent_core_repo())
            
        # Case 3: neither matches
        mock_exists.return_value = True
        with patch('builtins.open', new_callable=mock_open, read_data="- **Product:** custom-project\n"):
            self.assertFalse(changelog.is_agent_core_repo())

if __name__ == '__main__':
    unittest.main()
