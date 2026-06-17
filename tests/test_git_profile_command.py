import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile
import shutil

# Ensure the cli directory is in the import path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".agents", "scripts", "cli"))
import commands.git_profile as git_profile
import utils

class TestGitProfileCommand(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to act as workspace
        self.test_dir = tempfile.mkdtemp()
        self.orig_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Setup basic .agents folder
        self.agents_dir = os.path.join(self.test_dir, ".agents")
        os.makedirs(self.agents_dir)
        
        # Create a mock git folder to satisfy git repository check
        os.makedirs(os.path.join(self.test_dir, ".git"))
        
        # Create mock git_profiles configuration file
        self.profiles_file = os.path.join(self.agents_dir, "git_profiles")
        with open(self.profiles_file, 'w', encoding='utf-8') as f:
            f.write("profile1.name=User One\n")
            f.write("profile1.email=one@example.com\n")
            f.write("profile2.name=User Two\n")
            f.write("profile2.email=two@example.com\n")

    def tearDown(self):
        os.chdir(self.orig_cwd)
        shutil.rmtree(self.test_dir)

    @patch('subprocess.check_output')
    @patch('subprocess.run')
    @patch('utils.get_agents_dir')
    def test_rotation_prioritizes_current_config(self, mock_get_agents_dir, mock_run, mock_check_output):
        mock_get_agents_dir.return_value = self.agents_dir
        
        # Mock currently configured local email is 'one@example.com'
        def side_effect(args, **kwargs):
            if "config" in args and "user.email" in args:
                return b"one@example.com\n"
            elif "log" in args:
                return b"two@example.com\n" # Different from config to test prioritization
            return b""
        mock_check_output.side_effect = side_effect
        
        # Run git-profile rotate
        with patch('sys.exit') as mock_exit:
            git_profile.run(["git-profile", "rotate"])
            
            # Since current configured email is 'one@example.com', it should rotate to 'profile2'
            mock_run.assert_any_call(["git", "config", "--local", "user.name", "User Two"], check=True)
            mock_run.assert_any_call(["git", "config", "--local", "user.email", "two@example.com"], check=True)

    @patch('subprocess.check_output')
    @patch('subprocess.run')
    @patch('utils.get_agents_dir')
    def test_rotation_falls_back_to_git_log(self, mock_get_agents_dir, mock_run, mock_check_output):
        mock_get_agents_dir.return_value = self.agents_dir
        
        # Mock currently configured local email is unset (fails), but git log has 'one@example.com'
        def side_effect(args, **kwargs):
            if "config" in args and "user.email" in args:
                raise subprocess.CalledProcessError(1, args)
            elif "log" in args:
                return b"one@example.com\n"
            return b""
        mock_check_output.side_effect = side_effect
        
        # Run git-profile rotate
        with patch('sys.exit') as mock_exit:
            git_profile.run(["git-profile", "rotate"])
            
            # Should fall back to git log's 'one@example.com' and rotate to 'profile2'
            mock_run.assert_any_call(["git", "config", "--local", "user.name", "User Two"], check=True)
            mock_run.assert_any_call(["git", "config", "--local", "user.email", "two@example.com"], check=True)

if __name__ == '__main__':
    unittest.main()
