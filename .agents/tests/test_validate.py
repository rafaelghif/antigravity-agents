import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import io
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

    @patch('validate.validate_json_schema', return_value=True)
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="- **Version:** 2.192.0")
    def test_audit_critical_files(self, mock_file, mock_exists, mock_json_schema):
        # All exist
        mock_exists.return_value = True
        mock_exists.side_effect = None
        self.assertTrue(validate.audit_critical_files())
        
        # Missing critical file
        mock_exists.side_effect = lambda path: "rules.md" not in path
        self.assertFalse(validate.audit_critical_files())

    @patch('validate.validate_json_schema', return_value=True)
    @patch('os.path.exists', return_value=True)
    def test_audit_critical_files_version_mismatch(self, mock_exists, mock_json_schema):
        def mock_open_side_effect(path, *args, **kwargs):
            if "AGENTS.md" in path:
                return mock_open(read_data="- **Version:** 2.192.0")()
            elif "bootstrap.py" in path:
                return mock_open(read_data="AAC_VERSION = \"1.0.0\"")()
            else:
                return mock_open(read_data="- **Version:** 2.192.0")()
        with patch('builtins.open', side_effect=mock_open_side_effect):
            self.assertFalse(validate.audit_critical_files())

    @patch('os.path.exists')
    @patch('subprocess.run')
    @patch('validate.is_git_ignored')
    @patch('validate.is_ignored_by_antigravity')
    @patch('os.walk', return_value=[])
    def test_audit_secrets_and_ignored_files_rejections(self, mock_walk, mock_anti, mock_git, mock_run, mock_exists):
        # Mock exists to return False for git_profiles.json
        mock_exists.side_effect = lambda path: False if 'git_profiles.json' in path else True
        
        # Mock git diff returning staged files
        mock_run.return_value = MagicMock(returncode=0, stdout="A\tsrc/main.py\n")
        
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

    @patch('os.path.exists')
    @patch('subprocess.run')
    @patch('validate.is_git_ignored')
    @patch('validate.is_ignored_by_antigravity')
    @patch('os.walk')
    def test_audit_secrets_unignored_private_file(self, mock_walk, mock_anti, mock_git, mock_run, mock_exists):
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        # Simulate finding an unignored .env file
        mock_walk.return_value = [
            ('.', [], ['.env'])
        ]
        mock_git.return_value = False
        mock_anti.return_value = False
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
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        self.assertTrue(validate.audit_git_branch_alignment())

        # Scenario 4: On feature branch with pure number ID
        mock_get_branch.return_value = "feat/028"
        mock_exists.return_value = True
        mock_file_open.return_value.read.return_value = "id: issue-028\ntasks:\n- [x] Done\n"
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        self.assertTrue(validate.audit_git_branch_alignment())

        # Scenario 5: On feature branch with concatenated prefix and number
        mock_get_branch.return_value = "feat/issue028"
        self.assertTrue(validate.audit_git_branch_alignment())

        # Scenario 6: On feature branch with suffix description
        mock_get_branch.return_value = "feat/issue-028-some-description"
        self.assertTrue(validate.audit_git_branch_alignment())

        # Scenario 7: On feature branch with invalid ID pattern
        mock_get_branch.return_value = "some-random-branch"
        self.assertTrue(validate.audit_git_branch_alignment())

    @patch('validate.get_current_branch')
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_branch_type_enforcer_feat_mismatch(self, mock_file_open, mock_exists, mock_run, mock_get_branch):
        mock_get_branch.return_value = "feat/issue-028"
        mock_exists.return_value = True
        mock_file_open.return_value.read.return_value = "id: issue-028\ntasks:\n- [x] Done\n"
        
        # Mock git calls:
        # 1. show-ref (master verification): returncode=1
        # 2. git log: returncode=0, stdout="chore: some chore\n"
        # 3. git status --porcelain: returncode=0, stdout="" (is clean)
        mock_run.side_effect = [
            MagicMock(returncode=1),
            MagicMock(returncode=0, stdout="chore: some chore\n"),
            MagicMock(returncode=0, stdout="")
        ]
        self.assertFalse(validate.audit_git_branch_alignment())

    @patch('validate.get_current_branch')
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_branch_type_enforcer_fix_mismatch(self, mock_file_open, mock_exists, mock_run, mock_get_branch):
        mock_get_branch.return_value = "fix/issue-028"
        mock_exists.return_value = True
        mock_file_open.return_value.read.return_value = "id: issue-028\ntasks:\n- [x] Done\n"
        
        # Mock git calls:
        # 1. show-ref
        # 2. git log: returncode=0, stdout="feat: new feature\n"
        mock_run.side_effect = [
            MagicMock(returncode=1),
            MagicMock(returncode=0, stdout="feat: new feature\n")
        ]
        self.assertFalse(validate.audit_git_branch_alignment())

    @patch('validate.get_current_branch')
    @patch('commands.lock.load_locks')
    @patch('subprocess.run')
    def test_audit_module_locks(self, mock_run, mock_load_locks, mock_get_branch):
        # Scenario 1: On base branch main, skip lock checks
        mock_get_branch.return_value = "main"
        self.assertTrue(validate.audit_module_locks())
        
        # Scenario 2: On feature branch, no files staged
        mock_get_branch.return_value = "feat/issue-032"
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        self.assertTrue(validate.audit_module_locks())
        
        # Scenario 3: Staged file not locked
        mock_run.return_value = MagicMock(returncode=0, stdout="src/validate.py\n")
        mock_load_locks.return_value = {}
        self.assertFalse(validate.audit_module_locks())
        
        # Scenario 4: Staged file is locked by different branch
        mock_load_locks.return_value = {"validate": "feat/issue-abc"}
        self.assertFalse(validate.audit_module_locks())
        
        # Scenario 5: Staged file is locked by current branch
        mock_load_locks.return_value = {"validate": "feat/issue-032"}
        self.assertTrue(validate.audit_module_locks())

    @patch('os.getenv')
    @patch('validate.get_commit_sha')
    @patch('git_api.post_commit_status')
    @patch('sys.exit', side_effect=SystemExit)
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
    def test_run_validations_in_ci(self, m_commit, m_lock, m_test, m_lint, m_schema, m_sync, m_branch, m_link, m_secrets, m_crit, m_exit, m_post_status, m_sha, m_getenv):
        m_getenv.side_effect = lambda k: "true" if k in ("CI", "GITHUB_ACTIONS") else None
        m_sha.return_value = "dummy-sha-12345"
        
        with self.assertRaises(SystemExit):
            validate.run_validations()
        
        # Verify post_commit_status was called with success
        m_post_status.assert_any_call("dummy-sha-12345", "pending", description="Running AAC V3 Validation Guard...")
        m_post_status.assert_any_call("dummy-sha-12345", "success", description="AAC V3 Validation Guard passed successfully!")

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
    @patch('os.listdir', return_value=['issue_040.md'])
    @patch('builtins.open', new_callable=mock_open)
    @patch.dict('os.environ', {'SKIP_SUBTASK_AUDIT': 'true'})
    def test_audit_git_branch_alignment_with_skip_subtasks_env(self, mock_file_open, mock_listdir, mock_exists, mock_run, mock_get_branch):
        mock_get_branch.return_value = "feat/issue-040"
        mock_exists.return_value = True
        mock_file_open.return_value.read.return_value = "---\nid: issue-040\n---\n## Tasks\n- [ ] Task 1\n"
        self.assertTrue(validate.audit_git_branch_alignment())

    @patch('validate.get_current_branch')
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.listdir', return_value=['issue_040.md'])
    @patch('builtins.open', new_callable=mock_open)
    @patch('sys.argv', ['validate.py'])
    @patch.dict('os.environ', {'AAC_ENFORCE_SUBTASKS': 'true'}, clear=True)
    def test_audit_git_branch_alignment_fails_with_unresolved_subtasks(self, mock_file_open, mock_listdir, mock_exists, mock_run, mock_get_branch):
        mock_get_branch.return_value = "feat/issue-040"
        mock_exists.return_value = True
        mock_file_open.return_value.read.return_value = "---\nid: issue-040\n---\n## Tasks\n- [ ] Task 1\n"
        self.assertFalse(validate.audit_git_branch_alignment())

    @patch('validate.get_current_branch')
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.listdir', return_value=['issue_040.md'])
    @patch('builtins.open', new_callable=mock_open)
    @patch('sys.argv', ['validate.py'])
    @patch('sys.stdin.isatty', return_value=True)
    @patch.dict('os.environ', {'ANTIGRAVITY_NONINTERACTIVE': '1', 'AAC_ENFORCE_SUBTASKS': 'true'}, clear=True)
    def test_audit_git_branch_alignment_non_interactive_env(self, mock_isatty, mock_file_open, mock_listdir, mock_exists, mock_run, mock_get_branch):
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
    @patch('builtins.open')
    @patch('os.listdir', return_value=[])
    def test_audit_link_integrity(self, mock_listdir, mock_open_file, mock_exists):
        file_content = """
        Here is a link: file:///absolute/path/to/valid_file.py
        Here is another: [relative text](relative/valid.md)
        And an anchor range: [another relative](relative/valid.md#L5-L10)
        And a broken one: [broken link](missing.md)
        """
        def exists_side_effect(path):
            if "AGENTS.md" in path or "valid_file.py" in path or "valid.md" in path:
                return True
            return False
        mock_exists.side_effect = exists_side_effect

        mock_f_handle = MagicMock()
        mock_f_handle.read.return_value = file_content
        mock_f_handle.__enter__.return_value = mock_f_handle

        mock_ref_handle = MagicMock()
        mock_ref_handle.__enter__.return_value = mock_ref_handle
        mock_ref_handle.__iter__.side_effect = lambda: iter(["line"] * 15)

        def open_side_effect(path, *args, **kwargs):
            if "valid.md" in path:
                return mock_ref_handle
            return mock_f_handle

        mock_open_file.side_effect = open_side_effect

        self.assertFalse(validate.audit_link_integrity())

        def exists_side_effect_all(path):
            return True
        mock_exists.side_effect = exists_side_effect_all

        self.assertTrue(validate.audit_link_integrity())

        mock_ref_handle_short = MagicMock()
        mock_ref_handle_short.__enter__.return_value = mock_ref_handle_short
        mock_ref_handle_short.__iter__.side_effect = lambda: iter(["line"] * 5)
        def open_side_effect_short(path, *args, **kwargs):
            if "valid.md" in path:
                return mock_ref_handle_short
            return mock_f_handle
        mock_open_file.side_effect = open_side_effect_short

        self.assertFalse(validate.audit_link_integrity())

    @patch('os.path.exists', return_value=True)
    @patch('subprocess.run')
    @patch('builtins.open', new_callable=mock_open, read_data='{"profiles": [{"name": "corporate-work", "email": "developer@company.com", "active": true}]}')
    def test_audit_secrets_identity_repair_placeholder(self, mock_file, mock_sub, mock_exists):
        def side_effect(cmd, *args, **kwargs):
            cmd_str = " ".join(cmd)
            if "user.email" in cmd_str:
                return MagicMock(returncode=1, stdout="")
            elif "user.name" in cmd_str:
                return MagicMock(returncode=1, stdout="")
            return MagicMock(returncode=0)
            
        mock_sub.side_effect = side_effect
        
        res = validate.audit_secrets_and_ignored_files()
        self.assertTrue(res)
        
        sub_calls = [" ".join(call[0][0]) for call in mock_sub.call_args_list]
        self.assertTrue(any("user.email developer@antigravity.local" in cmd for cmd in sub_calls))
        self.assertTrue(any("user.name AAC Developer" in cmd for cmd in sub_calls))

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="outdated content")
    @patch('os.chmod')
    def test_audit_critical_files_hooks_repair(self, mock_chmod, mock_file, mock_exists):
        def exists_side_effect(path):
            if "json" in path:
                return False
            return True
            
        mock_exists.side_effect = exists_side_effect
        
        res = validate.audit_critical_files()
        self.assertTrue(res)
        mock_file().write.assert_called()

    @patch('shutil.which', side_effect=lambda name: "/usr/bin/php" if name == "php" else None)
    @patch('subprocess.run')
    def test_auto_lint_file_php(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        res = validate.auto_lint_file("test.php")
        self.assertTrue(res)
        mock_run.assert_called_once()
        self.assertIn("php", mock_run.call_args[0][0][0])
        
    @patch('shutil.which', side_effect=lambda name: "/usr/bin/eslint" if name == "eslint" else None)
    @patch('subprocess.run')
    def test_auto_lint_file_js(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        res = validate.auto_lint_file("test.js")
        self.assertTrue(res)
        mock_run.assert_called_once()
        self.assertIn("/usr/bin/eslint", mock_run.call_args[0][0][0])

    @patch('shutil.which', side_effect=lambda name: "/usr/bin/" + name if name in ("eslint", "tsc") else None)
    @patch('subprocess.run')
    def test_auto_lint_file_ts(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        res = validate.auto_lint_file("test.ts")
        self.assertTrue(res)
        self.assertEqual(mock_run.call_count, 2)
        
    @patch('py_compile.compile')
    @patch('shutil.which', side_effect=lambda name: "/usr/bin/" + name if name in ("flake8", "mypy") else None)
    @patch('subprocess.run')
    def test_auto_lint_file_python_mypy(self, mock_run, mock_which, mock_compile):
        mock_run.return_value = MagicMock(returncode=0)
        res = validate.auto_lint_file("test.py")
        self.assertTrue(res)
        self.assertEqual(mock_run.call_count, 2)

    @patch('shutil.which', side_effect=lambda name: "/usr/bin/javac" if name == "javac" else None)
    @patch('subprocess.run')
    def test_auto_lint_file_java(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        res = validate.auto_lint_file("test.java")
        self.assertTrue(res)
        mock_run.assert_called_once()
        self.assertIn("javac", mock_run.call_args[0][0][0])

    @patch('shutil.which', side_effect=lambda bin_name: "/usr/bin/shlint" if bin_name == "shlint" else None)
    @patch('subprocess.run')
    def test_run_project_lint_command(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        res = validate.run_project_lint_command("proj", "proj_path", "shlint file.js")
        self.assertTrue(res)
        mock_run.assert_called_once()

    @patch('shutil.which', side_effect=lambda bin_name: "/usr/bin/black" if bin_name == "black" else None)
    @patch('subprocess.run')
    def test_auto_format_file_python_black(self, mock_run, mock_which):
        validate.auto_format_file("test.py")
        mock_run.assert_called_once()
        self.assertIn("black", mock_run.call_args[0][0][0])
        
    @patch('shutil.which', side_effect=lambda bin_name: "/usr/bin/prettier" if bin_name == "prettier" else None)
    @patch('subprocess.run')
    def test_auto_format_file_js_prettier(self, mock_run, mock_which):
        validate.auto_format_file("test.js")
        mock_run.assert_called_once()
        self.assertIn("prettier", mock_run.call_args[0][0][0])

    @patch('shutil.which', side_effect=lambda name: "/usr/bin/gofmt" if name in ("gofmt", "go") else None)
    @patch('subprocess.run')
    def test_auto_lint_file_go(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        res = validate.auto_lint_file("test.go")
        self.assertTrue(res)
        self.assertEqual(mock_run.call_count, 2)
        
    @patch('shutil.which', side_effect=lambda name: "/usr/bin/rustfmt" if name in ("rustfmt", "rustc") else None)
    @patch('subprocess.run')
    def test_auto_lint_file_rust(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        res = validate.auto_lint_file("test.rs")
        self.assertTrue(res)
        self.assertEqual(mock_run.call_count, 2)

    @patch('validate.get_current_branch')
    @patch('validate.get_base_branch')
    @patch('subprocess.run')
    def test_audit_commit_messages_success(self, mock_run, mock_base_branch, mock_get_branch):
        mock_get_branch.return_value = "feat/issue-106"
        mock_base_branch.return_value = "main"
        mock_run.return_value = MagicMock(returncode=0, stdout="feat: correct subject line\n\nRefs: issue-106\nCompliance-Audit: passed\x00")
        self.assertTrue(validate.audit_commit_messages())

    @patch('validate.get_current_branch')
    @patch('validate.get_base_branch')
    @patch('subprocess.run')
    def test_audit_commit_messages_missing_refs(self, mock_run, mock_base_branch, mock_get_branch):
        mock_get_branch.return_value = "feat/issue-106"
        mock_base_branch.return_value = "main"
        mock_run.return_value = MagicMock(returncode=0, stdout="feat: missing refs trailer\x00")
        self.assertFalse(validate.audit_commit_messages())

    @patch('validate.get_current_branch')
    @patch('validate.get_base_branch')
    @patch('subprocess.run')
    def test_audit_commit_messages_invalid_conventional(self, mock_run, mock_base_branch, mock_get_branch):
        mock_get_branch.return_value = "feat/issue-106"
        mock_base_branch.return_value = "main"
        mock_run.return_value = MagicMock(returncode=0, stdout="bad subject: message\n\nRefs: issue-106\x00")
        self.assertFalse(validate.audit_commit_messages())

    @patch('validate.get_current_branch')
    @patch('validate.get_base_branch')
    @patch('subprocess.run')
    def test_audit_commit_messages_generic_subject(self, mock_run, mock_base_branch, mock_get_branch):
        mock_get_branch.return_value = "feat/issue-106"
        mock_base_branch.return_value = "main"
        mock_run.return_value = MagicMock(returncode=0, stdout="fix: issue-106\n\nRefs: issue-106\x00")
        self.assertFalse(validate.audit_commit_messages())

    @patch('os.environ.get')
    def test_audit_module_locks_bypassed_env(self, mock_env_get):
        mock_env_get.side_effect = lambda name, default=None: "true" if name == "SKIP_LOCK_AUDIT" else default
        self.assertTrue(validate.audit_module_locks())
        
        mock_env_get.side_effect = lambda name, default=None: "1" if name == "AAC_BYPASS_LOCKS" else default
        self.assertTrue(validate.audit_module_locks())

    @patch('os.path.exists')
    @patch('shutil.copy2')
    @patch('shutil.copytree')
    @patch('os.listdir')
    @patch('venv.create')
    @patch('tempfile.mkdtemp')
    def test_sandbox_manager_context(self, mock_mkdtemp, mock_venv_create, mock_listdir, mock_copytree, mock_copy2, mock_exists):
        mock_mkdtemp.return_value = "/tmp/fake_sandbox"
        mock_listdir.return_value = ["file1.py"]
        mock_exists.return_value = True
        
        with patch('os.chdir') as mock_chdir:
            with patch('os.getcwd', return_value="/original/cwd"):
                with validate.SandboxManager(enabled=True) as sandbox:
                    self.assertTrue(sandbox.enabled)
                    mock_venv_create.assert_called_once()
                    mock_chdir.assert_any_call("/tmp/fake_sandbox")

    @patch('subprocess.run')
    def test_make_skill_audit_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="Success")
        audit_func = validate.make_skill_audit("test_skill", "path/to/validate.py")
        result = audit_func()
        self.assertTrue(result)

    @patch('subprocess.run')
    def test_make_skill_audit_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="Failed", stderr="Error log")
        audit_func = validate.make_skill_audit("test_skill", "path/to/validate.py")
        result = audit_func()
        self.assertFalse(result)

    @patch('validate.get_current_branch')
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_audit_git_branch_alignment_contributor_mismatch(self, mock_open_file, mock_exists, mock_run, mock_get_branch):
        mock_get_branch.return_value = "feat/issue-225"
        mock_exists.side_effect = lambda path: True
        
        mock_issue_md = "---\nid: issue-225\ntitle: Test\nstatus: open\nassignee: dev-alice\n---\nTasks:\n- [x] Subtask 1\n"
        mock_profiles_json = json.dumps({
            "profiles": [
                {"name": "dev-alice", "email": "alice@corp.com", "active": True}
            ]
        })
        
        mock_open_file.side_effect = lambda path, *args, **kwargs: io.StringIO(mock_profiles_json) if "profiles" in path else io.StringIO(mock_issue_md)
        mock_run.return_value = MagicMock(returncode=0, stdout="bob@corp.com\n")
        
        self.assertFalse(validate.audit_git_branch_alignment())

    @patch('validate.get_current_branch')
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_audit_git_branch_alignment_contributor_match(self, mock_open_file, mock_exists, mock_run, mock_get_branch):
        mock_get_branch.return_value = "feat/issue-225"
        mock_exists.side_effect = lambda path: True
        
        mock_issue_md = "---\nid: issue-225\ntitle: Test\nstatus: open\nassignee: dev-alice\n---\nTasks:\n- [x] Subtask 1\n"
        mock_profiles_json = json.dumps({
            "profiles": [
                {"name": "dev-alice", "email": "alice@corp.com", "active": True}
            ]
        })
        
        mock_open_file.side_effect = lambda path, *args, **kwargs: io.StringIO(mock_profiles_json) if "profiles" in path else io.StringIO(mock_issue_md)
        mock_run.return_value = MagicMock(returncode=0, stdout="alice@corp.com\n")
        
        self.assertTrue(validate.audit_git_branch_alignment())

if __name__ == '__main__':
    unittest.main()
