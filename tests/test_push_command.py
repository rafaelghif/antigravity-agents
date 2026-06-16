import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure the cli directory is in the import path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".agents", "scripts", "cli"))
import commands.push as push

class TestPushCommand(unittest.TestCase):
    @patch('subprocess.run')
    @patch('subprocess.check_output')
    @patch('os.path.exists')
    @patch('utils.get_agents_dir')
    def test_push_with_no_validate(self, mock_get_agents_dir, mock_exists, mock_check_output, mock_run):
        mock_get_agents_dir.return_value = "/mock/agents"
        mock_exists.return_value = False # validate.sh and git_profiles don't exist
        mock_check_output.return_value = b"main\n"
        
        mock_run.return_value = MagicMock(returncode=0)
        
        # Test basic run with --no-validate
        with self.assertRaises(SystemExit) as cm:
            push.run(["push", "--no-validate"])
            
        self.assertEqual(cm.exception.code, 0)
        
        # Verify git push origin main was called
        mock_run.assert_any_call(["git", "push", "origin", "main"], env=unittest.mock.ANY)

    @patch('subprocess.run')
    @patch('subprocess.check_output')
    @patch('os.path.exists')
    @patch('utils.get_agents_dir')
    def test_push_with_force_and_no_validate(self, mock_get_agents_dir, mock_exists, mock_check_output, mock_run):
        mock_get_agents_dir.return_value = "/mock/agents"
        mock_exists.return_value = False
        mock_check_output.return_value = b"feature/branch\n"
        
        mock_run.return_value = MagicMock(returncode=0)
        
        with self.assertRaises(SystemExit) as cm:
            push.run(["push", "-n", "-f"])
            
        self.assertEqual(cm.exception.code, 0)
        
        mock_run.assert_any_call(["git", "push", "origin", "feature/branch", "--force"], env=unittest.mock.ANY)

    @patch('subprocess.run')
    @patch('subprocess.check_output')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="work.name=Dev\nwork.email=dev@work.com\nwork.ssh_key=~/.ssh/id_rsa_work\n")
    @patch('utils.get_agents_dir')
    def test_push_with_ssh_rotation(self, mock_get_agents_dir, mock_open, mock_exists, mock_check_output, mock_run):
        mock_get_agents_dir.return_value = "/mock/agents"
        
        # We mock exists such that validate.sh returns True, the git_profiles file exists, and the ssh key file exists.
        def exists_side_effect(path):
            if "validate.sh" in path:
                return False  # Skip validation execution to keep test simple
            if "git_profiles" in path:
                return True
            if "id_rsa_work" in path:
                return True
            return False
            
        mock_exists.side_effect = exists_side_effect
        
        mock_run.return_value = MagicMock(returncode=0)
        
        # Mock git configs
        # First call is git config user.email, second call is git rev-parse --abbrev-ref HEAD
        mock_check_output.side_effect = [b"dev@work.com\n", b"main\n"]
        
        with self.assertRaises(SystemExit) as cm:
            push.run(["push"])
            
        self.assertEqual(cm.exception.code, 0)
        
        # Verify git push origin main was called with rotated ssh key env variable
        called_args, called_kwargs = mock_run.call_args
        self.assertEqual(called_args[0], ["git", "push", "origin", "main"])
        self.assertIn("GIT_SSH_COMMAND", called_kwargs["env"])
        self.assertIn("id_rsa_work", called_kwargs["env"]["GIT_SSH_COMMAND"])

if __name__ == '__main__':
    unittest.main()
