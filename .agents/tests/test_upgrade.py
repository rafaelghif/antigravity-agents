import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import upgrade

def raise_system_exit(code=0):
    raise SystemExit(code)

class TestUpgradeCommand(unittest.TestCase):

    @patch('sys.exit', side_effect=raise_system_exit)
    @patch('subprocess.run')
    def test_upgrade_run_success(self, mock_sub, mock_exit):
        mock_sub.return_value = MagicMock(returncode=0)
        with self.assertRaises(SystemExit) as cm:
            upgrade.run([])
        self.assertEqual(cm.exception.code, 0)
        
        # Verify the paths passed to git checkout include the new ones
        checkout_call = next((call for call in mock_sub.call_args_list if 'checkout' in call[0][0]), None)
        self.assertIsNotNone(checkout_call)
        cmd_args = checkout_call[0][0]
        self.assertIn(".agents/skills/", cmd_args)
        self.assertIn(".agents/rules.md", cmd_args)
        self.assertIn("AGENTS.md", cmd_args)
        
    @patch('sys.exit', side_effect=raise_system_exit)
    @patch('subprocess.run')
    def test_upgrade_run_git_failure(self, mock_sub, mock_exit):
        def side_effect(cmd, **kwargs):
            if 'rev-parse' in cmd:
                return MagicMock(returncode=0)
            return MagicMock(returncode=1, stderr="Git fetch error")
        mock_sub.side_effect = side_effect
        
        with self.assertRaises(SystemExit) as cm:
            upgrade.run([])
        self.assertEqual(cm.exception.code, 1)

    @patch('os.environ.get', return_value="false")
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='{"last_check_timestamp": 9999999999.0}')
    @patch('time.time', return_value=9999999999.0)
    @patch('subprocess.run')
    def test_auto_upgrade_rate_limited(self, mock_sub, mock_time, mock_file_open, mock_exists, mock_env):
        upgrade.check_and_run_auto_upgrade()
        mock_sub.assert_not_called()

    @patch('os.environ.get', return_value="false")
    @patch('os.path.exists', return_value=False)
    @patch('time.time', return_value=1000.0)
    @patch('builtins.open', new_callable=mock_open)
    @patch('subprocess.run')
    def test_auto_upgrade_non_base_branch(self, mock_sub, mock_file_open, mock_time, mock_exists, mock_env):
        # Configure subprocess mocks: is-inside-work-tree=0, branch=feat/my-branch
        def side_effect(cmd, **kwargs):
            if 'rev-parse' in cmd:
                if '--is-inside-work-tree' in cmd:
                    return MagicMock(returncode=0)
                if '--abbrev-ref' in cmd:
                    return MagicMock(returncode=0, stdout="feat/my-branch\n")
            return MagicMock(returncode=0)
        mock_sub.side_effect = side_effect
        
        upgrade.check_and_run_auto_upgrade()
        fetch_call = any('fetch' in call[0][0] for call in mock_sub.call_args_list)
        self.assertFalse(fetch_call)

    @patch('os.environ.get', return_value="false")
    @patch('os.path.exists', return_value=False)
    @patch('time.time', return_value=1000.0)
    @patch('builtins.open', new_callable=mock_open)
    @patch('subprocess.run')
    def test_auto_upgrade_dirty_tree(self, mock_sub, mock_file_open, mock_time, mock_exists, mock_env):
        def side_effect(cmd, **kwargs):
            if 'rev-parse' in cmd:
                if '--is-inside-work-tree' in cmd:
                    return MagicMock(returncode=0)
                if '--abbrev-ref' in cmd:
                    return MagicMock(returncode=0, stdout="main\n")
            if 'status' in cmd:
                return MagicMock(returncode=0, stdout=" M helper.sh\n")
            return MagicMock(returncode=0)
        mock_sub.side_effect = side_effect
        
        upgrade.check_and_run_auto_upgrade()
        fetch_call = any('fetch' in call[0][0] for call in mock_sub.call_args_list)
        self.assertFalse(fetch_call)

    @patch('os.environ.get', return_value="false")
    @patch('os.path.exists', return_value=False)
    @patch('time.time', return_value=1000.0)
    @patch('builtins.open', new_callable=mock_open)
    @patch('subprocess.run')
    def test_auto_upgrade_success(self, mock_sub, mock_file_open, mock_time, mock_exists, mock_env):
        def side_effect(cmd, **kwargs):
            if 'rev-parse' in cmd:
                if '--is-inside-work-tree' in cmd:
                    return MagicMock(returncode=0)
                if '--abbrev-ref' in cmd:
                    return MagicMock(returncode=0, stdout="main\n")
            if 'status' in cmd:
                return MagicMock(returncode=0, stdout="")
            if 'remote' in cmd:
                return MagicMock(returncode=0, stdout="https://github.com/my/repo.git\n")
            if 'fetch' in cmd:
                return MagicMock(returncode=0)
            if 'merge-base' in cmd:
                return MagicMock(returncode=0)
            if 'diff' in cmd:
                return MagicMock(returncode=1)
            if 'checkout' in cmd:
                return MagicMock(returncode=0)
            return MagicMock(returncode=0)
        mock_sub.side_effect = side_effect
        
        upgrade.check_and_run_auto_upgrade()
        checkout_call = any('checkout' in call[0][0] for call in mock_sub.call_args_list)
        self.assertTrue(checkout_call)

if __name__ == '__main__':
    unittest.main()
