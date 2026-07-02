import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os

# Inject scripts folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
import validate

class TestValidate(unittest.TestCase):
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="node_modules/\n*.log\n# comment\n")
    def test_parse_antigravity_ignore(self, mock_file, mock_exists):
        mock_exists.return_value = True
        patterns = validate.parse_antigravity_ignore()
        self.assertEqual(len(patterns), 2)
        # Test matching
        self.assertTrue(validate.is_ignored_by_antigravity("src/node_modules/foo", patterns))
        self.assertTrue(validate.is_ignored_by_antigravity("error.log", patterns))
        self.assertFalse(validate.is_ignored_by_antigravity("src/main.py", patterns))

    @patch('subprocess.run')
    def test_is_git_ignored(self, mock_run):
        # Mock git check-ignore returns 0 (ignored)
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(validate.is_git_ignored("ignored_file.txt"))
        
        # Mock git check-ignore returns 1 (not ignored)
        mock_run.return_value = MagicMock(returncode=1)
        self.assertFalse(validate.is_git_ignored("normal_file.txt"))

    @patch('os.path.exists')
    def test_audit_critical_files(self, mock_exists):
        # All exist
        mock_exists.return_value = True
        self.assertTrue(validate.audit_critical_files())
        
        # Missing critical file
        mock_exists.side_effect = lambda path: "rules.md" not in path
        self.assertFalse(validate.audit_critical_files())

    @patch('os.path.exists')
    @patch('subprocess.run')
    @patch('validate.is_git_ignored')
    @patch('validate.is_ignored_by_antigravity')
    def test_audit_secrets_and_ignored_files_rejections(self, mock_anti, mock_git, mock_run, mock_exists):
        # Mock exists to return False for git_profiles.json
        mock_exists.side_effect = lambda path: False if 'git_profiles.json' in path else True
        
        # Mock git diff returning staged files
        mock_run.return_value = MagicMock(returncode=0, stdout="src/main.py\n")
        
        # Scenario 1: normal file
        mock_git.return_value = False
        mock_anti.return_value = False
        self.assertTrue(validate.audit_secrets_and_ignored_files())
        
        # Scenario 2: git ignored file staged
        mock_git.return_value = True
        mock_anti.return_value = False
        self.assertFalse(validate.audit_secrets_and_ignored_files())
        
        # Scenario 3: antigravity ignored file staged
        mock_git.return_value = False
        mock_anti.return_value = True
        self.assertFalse(validate.audit_secrets_and_ignored_files())

    @patch('validate.get_current_branch')
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_audit_git_branch_alignment(self, mock_file_open, mock_exists, mock_run, mock_get_branch):
        # Scenario 1: On main branch and clean git status
        mock_get_branch.return_value = "main"
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        self.assertTrue(validate.audit_git_branch_alignment())

        # Scenario 2: On main branch and dirty git status
        mock_run.return_value = MagicMock(returncode=0, stdout=" M src/main.py\n")
        self.assertFalse(validate.audit_git_branch_alignment())

        # Scenario 3: On feature branch with valid ID, issue files exist
        mock_get_branch.return_value = "feat/issue-028"
        mock_exists.return_value = True
        mock_file_open.return_value.read.return_value = "id: issue-028\ntasks:\n- [x] Done\n"
        self.assertTrue(validate.audit_git_branch_alignment())

        # Scenario 4: On feature branch with invalid ID pattern
        mock_get_branch.return_value = "some-random-branch"
        self.assertFalse(validate.audit_git_branch_alignment())

    @patch('validate.get_current_branch')
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_audit_module_locks(self, mock_file_open, mock_exists, mock_run, mock_get_branch):
        # Scenario 1: On base branch main, skip lock checks
        mock_get_branch.return_value = "main"
        self.assertTrue(validate.audit_module_locks())
        
        # Scenario 2: On feature branch, no files staged
        mock_get_branch.return_value = "feat/issue-032"
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        self.assertTrue(validate.audit_module_locks())
        
        # Scenario 3: Staged file not locked
        mock_run.return_value = MagicMock(returncode=0, stdout="src/validate.py\n")
        mock_exists.return_value = True
        mock_file_open.return_value.read.return_value = '{}'
        self.assertFalse(validate.audit_module_locks())
        
        # Scenario 4: Staged file is locked by different branch
        mock_file_open.return_value.read.return_value = '{"validate": "feat/issue-abc"}'
        self.assertFalse(validate.audit_module_locks())
        
        # Scenario 5: Staged file is locked by current branch
        mock_file_open.return_value.read.return_value = '{"validate": "feat/issue-032"}'
        self.assertTrue(validate.audit_module_locks())

    @patch('os.getenv')
    @patch('validate.get_commit_sha')
    @patch('git_api.post_commit_status')
    @patch('sys.exit')
    @patch('validate.audit_critical_files', return_value=True)
    @patch('validate.audit_secrets_and_ignored_files', return_value=True)
    @patch('validate.audit_link_integrity', return_value=True)
    @patch('validate.audit_git_branch_alignment', return_value=True)
    @patch('validate.audit_workspace_sync', return_value=True)
    @patch('validate.audit_task_board_schema', return_value=True)
    @patch('validate.audit_static_linting', return_value=True)
    @patch('validate.audit_unit_tests', return_value=True)
    @patch('validate.audit_module_locks', return_value=True)
    def test_run_validations_in_ci(self, m_lock, m_test, m_lint, m_schema, m_sync, m_branch, m_link, m_secrets, m_crit, m_exit, m_post_status, m_sha, m_getenv):
        m_getenv.side_effect = lambda k: "true" if k in ("CI", "GITHUB_ACTIONS") else None
        m_sha.return_value = "dummy-sha-12345"
        
        validate.run_validations()
        
        # Verify post_commit_status was called with success
        m_post_status.assert_any_call("dummy-sha-12345", "pending", description="Running AAC V2 Validation Guard...")
        m_post_status.assert_any_call("dummy-sha-12345", "success", description="AAC V2 Validation Guard passed successfully!")

    @patch('validate.get_current_branch')
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('sys.argv', ['validate.py', '--skip-subtasks'])
    def test_audit_git_branch_alignment_with_skip_subtasks_flag(self, mock_file_open, mock_exists, mock_run, mock_get_branch):
        mock_get_branch.return_value = "feat/issue-040"
        mock_exists.return_value = True
        mock_file_open.return_value.read.return_value = "---\nid: issue-040\n---\n## Tasks\n- [ ] Task 1\n"
        self.assertTrue(validate.audit_git_branch_alignment())

    @patch('validate.get_current_branch')
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch.dict('os.environ', {'SKIP_SUBTASK_AUDIT': 'true'})
    def test_audit_git_branch_alignment_with_skip_subtasks_env(self, mock_file_open, mock_exists, mock_run, mock_get_branch):
        mock_get_branch.return_value = "feat/issue-040"
        mock_exists.return_value = True
        mock_file_open.return_value.read.return_value = "---\nid: issue-040\n---\n## Tasks\n- [ ] Task 1\n"
        self.assertTrue(validate.audit_git_branch_alignment())

    @patch('validate.get_current_branch')
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('sys.argv', ['validate.py'])
    def test_audit_git_branch_alignment_fails_with_unresolved_subtasks(self, mock_file_open, mock_exists, mock_run, mock_get_branch):
        mock_get_branch.return_value = "feat/issue-040"
        mock_exists.return_value = True
        mock_file_open.return_value.read.return_value = "---\nid: issue-040\n---\n## Tasks\n- [ ] Task 1\n"
        self.assertFalse(validate.audit_git_branch_alignment())

    @patch('os.path.exists', return_value=True)
    @patch('subprocess.run')
    @patch('builtins.open', new_callable=mock_open, read_data='{"profiles": [{"name": "p1", "email": "p1@test.com", "active": true, "signing_key": "4A1D5B"}]}')
    def test_audit_secrets_identity_repair_and_gpg_disable(self, mock_file, mock_sub, mock_exists):
        def side_effect(cmd, *args, **kwargs):
            cmd_str = " ".join(cmd)
            if "user.email" in cmd_str:
                return MagicMock(returncode=1, stdout="")
            elif "user.name" in cmd_str:
                return MagicMock(returncode=1, stdout="")
            elif "commit.gpgsign" in cmd_str:
                return MagicMock(returncode=0, stdout="true\n")
            elif "user.signingkey" in cmd_str:
                return MagicMock(returncode=0, stdout="4A1D5B\n")
            elif "gpg" in cmd_str:
                return MagicMock(returncode=1)
            return MagicMock(returncode=0)
            
        mock_sub.side_effect = side_effect
        
        res = validate.audit_secrets_and_ignored_files()
        self.assertTrue(res)
        
        sub_calls = [" ".join(call[0][0]) for call in mock_sub.call_args_list]
        self.assertTrue(any("user.email p1@test.com" in cmd for cmd in sub_calls))
        self.assertTrue(any("user.name p1" in cmd for cmd in sub_calls))
        self.assertTrue(any("commit.gpgsign false" in cmd for cmd in sub_calls))

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="outdated content")
    @patch('os.chmod')
    def test_audit_critical_files_hooks_repair(self, mock_chmod, mock_file, mock_exists):
        def exists_side_effect(path):
            if ".git/hooks" in path:
                return True
            return True
            
        mock_exists.side_effect = exists_side_effect
        
        res = validate.audit_critical_files()
        self.assertTrue(res)
        mock_file().write.assert_called()

    @patch('shutil.which', return_value="/usr/bin/php")
    @patch('subprocess.run')
    def test_auto_lint_file_php(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        res = validate.auto_lint_file("test.php")
        self.assertTrue(res)
        mock_run.assert_called_once()
        self.assertIn("php", mock_run.call_args[0][0])
        
    @patch('shutil.which', return_value="/usr/bin/eslint")
    @patch('subprocess.run')
    def test_auto_lint_file_js(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        res = validate.auto_lint_file("test.js")
        self.assertTrue(res)
        mock_run.assert_called_once()
        self.assertIn("/usr/bin/eslint", mock_run.call_args[0][0])

    @patch('shutil.which', return_value="/usr/bin/shlint")
    @patch('subprocess.run')
    def test_run_project_lint_command(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        res = validate.run_project_lint_command("proj", "proj_path", "shlint file.js")
        self.assertTrue(res)
        mock_run.assert_called_once()

if __name__ == '__main__':
    unittest.main()
