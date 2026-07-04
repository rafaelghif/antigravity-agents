import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os

# Inject CLI commands folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import dashboard
import mimetypes
mimetypes.init()

class TestDashboardCommand(unittest.TestCase):
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="---\nid: issue-126\ntitle: \"My Test Issue\"\nstatus: open\ngithub_number: 12\n---\n")
    def test_get_issue_frontmatter(self, mock_file, mock_exists):
        fm = dashboard.get_issue_frontmatter(".agents/issues/issue_126.md")
        self.assertEqual(fm.get("id"), "issue-126")
        self.assertEqual(fm.get("title"), "My Test Issue")
        self.assertEqual(fm.get("status"), "open")
        self.assertEqual(fm.get("github_number"), "12")

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('subprocess.run')
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
    def test_get_dashboard_data(self, mock_commit, mock_locks, mock_tests, mock_lint, mock_board, mock_sync, mock_git, mock_link, mock_sec, mock_crit, mock_sub, mock_file, mock_exists):
        # Configure subprocess for git branch
        mock_sub.return_value = MagicMock(returncode=0, stdout="feat/issue-126")
        
        mock_file.return_value.read.side_effect = [
            "- **Version:** 2.106.0", # AGENTS.md
            '{"app/models/user.py": {"branch": "feat/issue-126", "timestamp": "2026-07-02 21:00"}}', # locks.json
            "---\nid: issue-126\ntitle: \"Active Task\"\nstatus: open\n---\n- [ ] Subtask 1", # issue_126.md (get_issue_frontmatter)
            "---\nid: issue-126\ntitle: \"Active Task\"\nstatus: open\n---\n- [ ] Subtask 1", # issue_126.md (tasks extraction)
            "# Lessons\n## Lessons Learned\n- My Lesson", # lessons-learned.md
            "## 5. Synthesized Rules (Self-Learning Memory)\n- My Synthesized Rule", # rules.md
            "## [2.106.0] - 2026-07-02" # CHANGELOG.md
        ]
        
        data = dashboard.get_dashboard_data()
        
        self.assertEqual(data["version"], "2.106.0")
        self.assertEqual(len(data["locks"]), 1)
        self.assertEqual(data["locks"][0]["module"], "app/models/user.py")
        self.assertEqual(data["active_issue"]["id"], "ISSUE-126")
        self.assertEqual(data["active_issue"]["title"], "Active Task")
        self.assertIn("My Lesson", data["lessons"])
        self.assertIn("My Synthesized Rule", data["rules"])
        self.assertTrue(data["compliance"]["Critical Files"])

    @patch('subprocess.run')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('issue.sync_board_with_issues')
    def test_toggle_issue_task(self, mock_sync, mock_file_open, mock_exists, mock_sub):
        mock_sub.return_value = MagicMock(returncode=0, stdout="feat/issue-130\n")
        
        file_content = "---\nid: issue-130\ntitle: \"Modernize Dashboard\"\nstatus: open\n---\n- [ ] Subtask 1\n- [ ] Subtask 2"
        mock_file_open.return_value.read.return_value = file_content
        
        success = dashboard.toggle_issue_task(1, True)
        self.assertTrue(success)
        
        # Verify it wrote back the content with [x] for Subtask 2
        write_args = "".join(call.args[0] for call in mock_file_open.return_value.write.call_args_list)
        self.assertIn("- [x] Subtask 2", write_args)
        self.assertIn("- [ ] Subtask 1", write_args)
        mock_sync.assert_called_once()

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('builtins.open', new_callable=mock_open, read_data=b"my html content")
    def test_serve_static_file_success(self, mock_file_open, mock_isfile, mock_exists):
        import io
        mock_exists.return_value = True
        mock_isfile.return_value = True
        
        handler = MagicMock()
        handler.wfile = io.BytesIO()
        
        dashboard.DashboardHandler.serve_static_file(handler, "/index.html")
        
        handler.send_response.assert_called_with(200)
        handler.send_header.assert_any_call('Content-Type', 'text/html; charset=utf-8')
        handler.wfile.seek(0)
        self.assertEqual(handler.wfile.read(), b"my html content")

    def test_serve_static_file_traversal_blocked(self):
        import io
        handler = MagicMock()
        handler.wfile = io.BytesIO()
        
        dashboard.DashboardHandler.serve_static_file(handler, "/../../../../etc/passwd")
        
        handler.send_response.assert_called_with(403)
        handler.wfile.seek(0)
        self.assertIn(b"Forbidden: Directory Traversal Blocked", handler.wfile.read())

    def test_serve_static_file_traversal_prefix_blocked(self):
        import io
        handler = MagicMock()
        handler.wfile = io.BytesIO()
        
        dashboard.DashboardHandler.serve_static_file(handler, "/../dashboard-alternative/index.html")
        
        handler.send_response.assert_called_with(403)
        handler.wfile.seek(0)
        self.assertIn(b"Forbidden: Directory Traversal Blocked", handler.wfile.read())

    @patch('os.path.exists', return_value=False)
    def test_serve_static_file_not_found(self, mock_exists):
        import io
        handler = MagicMock()
        handler.wfile = io.BytesIO()
        
        dashboard.DashboardHandler.serve_static_file(handler, "/nonexistent.html")
        
        handler.send_response.assert_called_with(404)
        handler.wfile.seek(0)
        self.assertIn(b"Not Found", handler.wfile.read())

    @unittest.skipIf(os.getenv("IN_AUDIT_TEST") == "true", "Skip async dashboard test during validation check to prevent infinite recursion")
    @patch('dashboard.run_silent_validation')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('subprocess.run')
    def test_get_dashboard_data_async_force(self, mock_sub, mock_file, mock_exists, mock_silent_val):
        mock_sub.return_value = MagicMock(returncode=0, stdout="feat/issue-126")
        mock_file.return_value.read.return_value = "- **Version:** 2.106.0"
        import time
        def slow_validation(*args, **kwargs):
            time.sleep(0.1)
            return {"Critical Files": True}
        mock_silent_val.side_effect = slow_validation
        
        # Reset global state to clean state
        dashboard.audit_in_progress = False
        
        # Force audit check - should spawn a thread and return immediately
        data = dashboard.get_dashboard_data(force=True)
        
        # Immediate auditing state should be True
        self.assertTrue(data["auditing"])
        
        # Wait up to 1 second for the background thread to finish
        retries = 10
        while dashboard.audit_in_progress and retries > 0:
            time.sleep(0.1)
            retries -= 1
            
        self.assertFalse(dashboard.audit_in_progress)
        
        # Calling get_dashboard_data now should return auditing: False
        data_after = dashboard.get_dashboard_data(force=False)
        self.assertFalse(data_after["auditing"])

    @patch('dashboard.profile_cmd.load_profiles')
    @patch('dashboard.profile_cmd.save_profiles')
    @patch('dashboard.profile_cmd.apply_git_config')
    def test_switch_active_profile(self, mock_apply, mock_save, mock_load):
        mock_load.return_value = {
            "profiles": [
                {"name": "p1", "email": "p1@mail.com", "active": True},
                {"name": "p2", "email": "p2@mail.com", "active": False}
            ]
        }
        success, msg = dashboard.switch_active_profile("p2")
        self.assertTrue(success)
        mock_save.assert_called_once()
        saved_data = mock_save.call_args[0][0]
        self.assertFalse(saved_data["profiles"][0]["active"])
        self.assertTrue(saved_data["profiles"][1]["active"])
        mock_apply.assert_called_once_with(saved_data["profiles"][1])

    @patch('dashboard.profile_cmd.load_profiles')
    @patch('dashboard.profile_cmd.save_profiles')
    def test_add_new_profile(self, mock_save, mock_load):
        mock_load.return_value = {
            "profiles": [
                {"name": "p1", "email": "p1@mail.com", "active": True}
            ]
        }
        success, msg = dashboard.add_new_profile({
            "name": "p2",
            "email": "p2@mail.com",
            "signing_key": "4A1D5B"
        })
        self.assertTrue(success)
        mock_save.assert_called_once()
        saved_data = mock_save.call_args[0][0]
        self.assertEqual(len(saved_data["profiles"]), 2)
        self.assertEqual(saved_data["profiles"][1]["name"], "p2")
        self.assertEqual(saved_data["profiles"][1]["signing_key"], "4A1D5B")

    @patch('dashboard.profile_cmd.load_profiles')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="ssh-ed25519 AAAAB3NzaC1yc2EA...")
    def test_get_ssh_public_key(self, mock_file, mock_exists, mock_load):
        mock_load.return_value = {
            "profiles": [
                {"name": "p1", "email": "p1@mail.com", "active": True, "ssh_key_path": "~/.ssh/id_ed25519_p1"}
            ]
        }
        pub_key, err = dashboard.get_ssh_public_key("p1")
        self.assertIsNone(err)
        self.assertEqual(pub_key, "ssh-ed25519 AAAAB3NzaC1yc2EA...")

    @patch('dashboard.lock_cmd.load_locks')
    @patch('dashboard.lock_cmd.save_locks')
    @patch('subprocess.run')
    def test_acquire_module_lock(self, mock_sub, mock_save, mock_load):
        mock_sub.return_value = MagicMock(returncode=0, stdout="feat/issue-141")
        mock_load.return_value = {}
        success, msg = dashboard.acquire_module_lock("bootstrap")
        self.assertTrue(success)
        mock_save.assert_called_once_with({"bootstrap": "feat/issue-141"})

    @patch('dashboard.lock_cmd.load_locks')
    @patch('dashboard.lock_cmd.save_locks')
    def test_release_module_lock(self, mock_save, mock_load):
        mock_load.return_value = {"bootstrap": "feat/issue-141"}
        success, msg = dashboard.release_module_lock("bootstrap")
        self.assertTrue(success)
        mock_save.assert_called_once_with({})

    @patch('dashboard.learn_cmd.record_lesson')
    @patch('dashboard.run_sync_workspace')
    def test_record_learned_lesson(self, mock_sync, mock_record):
        success, msg = dashboard.record_learned_lesson("My lesson", "Testing")
        self.assertTrue(success)
        mock_record.assert_called_once_with("My lesson", "Testing")
        mock_sync.assert_called_once()

    @patch('importlib.util.spec_from_file_location')
    @patch('os.path.exists', return_value=True)
    def test_run_sync_workspace(self, mock_exists, mock_spec):
        mock_sync_module = MagicMock()
        mock_spec.return_value.loader.exec_module = lambda m: None
        mock_spec.return_value = MagicMock()
        with patch('importlib.util.module_from_spec', return_value=mock_sync_module):
            success, msg = dashboard.run_sync_workspace()
            self.assertTrue(success)
            mock_sync_module.sync_skills_to_agents_md.assert_called_once()
            mock_sync_module.sync_adrs_to_architecture_md.assert_called_once()
            mock_sync_module.sync_lessons_to_rules.assert_called_once()

    @patch('dashboard.ThreadingHTTPServer')
    @patch('threading.Thread')
    @patch('webbrowser.open_new_tab')
    def test_dashboard_run_args(self, mock_open_tab, mock_thread, mock_server):
        mock_server_instance = MagicMock()
        mock_server.return_value = mock_server_instance
        old_env = os.environ.get("AAC_DASHBOARD_ALLOW_EXTERNAL")
        try:
            # Test 1: Default arguments
            with patch('sys.exit') as mock_exit:
                dashboard.run([])
                mock_server.assert_called_with(('127.0.0.1', 8000), dashboard.DashboardHandler)
                mock_open_tab.assert_called_with('http://127.0.0.1:8000/')
                
            # Test 2: Custom host and port
            mock_server.reset_mock()
            mock_open_tab.reset_mock()
            with patch('sys.exit') as mock_exit:
                dashboard.run(['--host', '0.0.0.0', '--port', '9000'])
                mock_server.assert_called_with(('0.0.0.0', 9000), dashboard.DashboardHandler)
                mock_open_tab.assert_not_called()
                self.assertEqual(os.environ.get("AAC_DASHBOARD_ALLOW_EXTERNAL"), "true")
        finally:
            if old_env is None:
                os.environ.pop("AAC_DASHBOARD_ALLOW_EXTERNAL", None)
            else:
                os.environ["AAC_DASHBOARD_ALLOW_EXTERNAL"] = old_env

if __name__ == '__main__':
    unittest.main()
