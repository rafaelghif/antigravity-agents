import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os

# Inject CLI commands folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import profile

class TestProfileCommand(unittest.TestCase):
    
    @patch('os.path.exists')
    @patch('shutil.copy')
    def test_ensure_profiles_file_copy_example(self, mock_copy, mock_exists):
        # Exists example but not target
        mock_exists.side_effect = lambda path: path == profile.PROFILES_EXAMPLE
        profile.ensure_profiles_file()
        mock_copy.assert_called_once_with(profile.PROFILES_EXAMPLE, profile.PROFILES_FILE)

    @patch('builtins.open', new_callable=mock_open, read_data='# Comment line\n{"profiles": [{"name": "test", "email": "test@test.com", "active": false}]}')
    @patch('os.path.exists')
    def test_load_profiles_stripping_comments(self, mock_exists, mock_file):
        mock_exists.return_value = True
        data = profile.load_profiles()
        self.assertEqual(len(data["profiles"]), 1)
        self.assertEqual(data["profiles"][0]["name"], "test")

    @patch('builtins.open', new_callable=mock_open)
    def test_save_profiles(self, mock_file):
        data = {"profiles": [{"name": "p1", "email": "p1@test.com", "active": True}]}
        profile.save_profiles(data)
        mock_file.assert_called_once_with(profile.PROFILES_FILE, 'w', encoding='utf-8')
        mock_file().write.assert_called()

    @patch('builtins.print')
    @patch('profile.load_profiles')
    def test_handle_list(self, mock_load, mock_print):
        mock_load.return_value = {
            "profiles": [
                {"name": "p1", "email": "p1@test.com", "active": True},
                {"name": "p2", "email": "p2@test.com", "active": False}
            ]
        }
        profile.handle_list([])
        # Verify that print was called with active profile highlighted
        printed_args = [call[0][0] for call in mock_print.call_args_list]
        self.assertTrue(any("*" in arg and "p1" in arg for arg in printed_args))
        self.assertTrue(any("p2" in arg for arg in printed_args))

    @patch('subprocess.run')
    @patch('profile.load_profiles')
    @patch('profile.save_profiles')
    def test_handle_switch_success(self, mock_save, mock_load, mock_sub):
        mock_load.return_value = {
            "profiles": [
                {"name": "p1", "email": "p1@test.com", "active": True},
                {"name": "p2", "email": "p2@test.com", "active": False}
            ]
        }
        # Mock git repo check and config updates
        mock_sub.return_value = MagicMock(returncode=0)
        
        profile.handle_switch(["p2"])
        
        # Verify save_profiles updated active status
        saved_data = mock_save.call_args[0][0]
        self.assertFalse(saved_data["profiles"][0]["active"])
        self.assertTrue(saved_data["profiles"][1]["active"])
        
        # Verify git local configs were invoked
        sub_calls = [call[0][0] for call in mock_sub.call_args_list]
        self.assertTrue(any("user.name" in cmd and "p2" in cmd for cmd in sub_calls))
        self.assertTrue(any("user.email" in cmd and "p2@test.com" in cmd for cmd in sub_calls))

    @patch('os.path.exists')
    @patch('subprocess.run')
    @patch('profile.load_profiles')
    @patch('profile.save_profiles')
    def test_handle_switch_with_ssh_key(self, mock_save, mock_load, mock_sub, mock_exists):
        mock_exists.return_value = True
        mock_load.return_value = {
            "profiles": [
                {"name": "p1", "email": "p1@test.com", "active": True},
                {"name": "p2", "email": "p2@test.com", "active": False, "ssh_key_path": "~/.ssh/id_rsa_p2"}
            ]
        }
        mock_sub.return_value = MagicMock(returncode=0)
        
        profile.handle_switch(["p2"])
        
        sub_calls = [call[0][0] for call in mock_sub.call_args_list]
        self.assertTrue(any("core.sshCommand" in " ".join(cmd) and "id_rsa_p2" in " ".join(cmd) for cmd in sub_calls))

    @patch('subprocess.run')
    @patch('profile.load_profiles')
    @patch('profile.save_profiles')
    def test_handle_switch_gpg_success(self, mock_save, mock_load, mock_sub):
        mock_load.return_value = {
            "profiles": [
                {"name": "p1", "email": "p1@test.com", "active": True},
                {"name": "p2", "email": "p2@test.com", "active": False, "signing_key": "4A1D5B"}
            ]
        }
        def side_effect(cmd, *args, **kwargs):
            if cmd[0] == "gpg":
                return MagicMock(returncode=0)
            return MagicMock(returncode=0)
        mock_sub.side_effect = side_effect
        
        profile.handle_switch(["p2"])
        
        saved_data = mock_save.call_args[0][0]
        self.assertTrue(saved_data["profiles"][1]["active"])

    @patch('sys.exit', side_effect=SystemExit)
    @patch('subprocess.run')
    @patch('profile.load_profiles')
    @patch('profile.save_profiles')
    def test_handle_switch_gpg_failure(self, mock_save, mock_load, mock_sub, mock_exit):
        mock_load.return_value = {
            "profiles": [
                {"name": "p1", "email": "p1@test.com", "active": True},
                {"name": "p2", "email": "p2@test.com", "active": False, "signing_key": "4A1D5B"}
            ]
        }
        def side_effect(cmd, *args, **kwargs):
            if cmd[0] == "gpg":
                return MagicMock(returncode=1)
            return MagicMock(returncode=0)
        mock_sub.side_effect = side_effect
        
        with self.assertRaises(SystemExit):
            profile.handle_switch(["p2"])
        mock_exit.assert_called_once_with(1)

    @patch('subprocess.run')
    @patch('profile.load_profiles')
    @patch('profile.save_profiles')
    def test_handle_switch_gpg_override(self, mock_save, mock_load, mock_sub):
        mock_load.return_value = {
            "profiles": [
                {"name": "p1", "email": "p1@test.com", "active": True},
                {"name": "p2", "email": "p2@test.com", "active": False, "signing_key": "4A1D5B"}
            ]
        }
        def side_effect(cmd, *args, **kwargs):
            if cmd[0] == "gpg":
                return MagicMock(returncode=1) # should not run gpg
            return MagicMock(returncode=0)
        mock_sub.side_effect = side_effect
        
        profile.handle_switch(["p2", "--force-no-gpg"])
        
        saved_data = mock_save.call_args[0][0]
        self.assertTrue(saved_data["profiles"][1]["active"])

    @patch('sys.exit', side_effect=SystemExit)
    @patch('profile.load_profiles')
    def test_handle_switch_not_found(self, mock_load, mock_exit):
        mock_load.return_value = {"profiles": []}
        with self.assertRaises(SystemExit):
            profile.handle_switch(["non-existent"])
        mock_exit.assert_called_once_with(1)

    @patch('profile.load_profiles')
    @patch('profile.save_profiles')
    @patch('profile.handle_switch')
    def test_handle_add_success(self, mock_switch, mock_save, mock_load):
        mock_load.return_value = {"profiles": []}
        profile.handle_add(["new-prof", "new@prof.com", "--switch"])
        
        # Verify save was called with the new profile added
        saved_data = mock_save.call_args[0][0]
        self.assertEqual(len(saved_data["profiles"]), 1)
        self.assertEqual(saved_data["profiles"][0]["name"], "new-prof")
        self.assertEqual(saved_data["profiles"][0]["email"], "new@prof.com")
        
        # Verify switch was called because of --switch flag
        mock_switch.assert_called_once_with(["new-prof"])

    @patch('sys.exit', side_effect=SystemExit)
    @patch('profile.load_profiles')
    def test_handle_add_validation_failures(self, mock_load, mock_exit):
        # Invalid email
        with self.assertRaises(SystemExit):
            profile.handle_add(["new-prof", "invalid-email"])
        mock_exit.assert_called_with(1)
        mock_exit.reset_mock()
        
        # Invalid name
        with self.assertRaises(SystemExit):
            profile.handle_add(["new prof with space", "test@test.com"])
        mock_exit.assert_called_with(1)
        mock_exit.reset_mock()
        
        # Duplicate name
        mock_load.return_value = {"profiles": [{"name": "existing", "email": "test@test.com"}]}
        with self.assertRaises(SystemExit):
            profile.handle_add(["existing", "new@test.com"])
        mock_exit.assert_called_with(1)

    @patch('subprocess.run')
    @patch('profile.load_profiles')
    @patch('profile.save_profiles')
    def test_handle_switch_with_git_token(self, mock_save, mock_load, mock_sub):
        mock_load.return_value = {
            "profiles": [
                {"name": "p1", "email": "p1@test.com", "active": True},
                {"name": "p2", "email": "p2@test.com", "active": False, "git_token": "ghp_realSecretToken123"}
            ]
        }
        mock_sub.return_value = MagicMock(returncode=0)
        
        profile.handle_switch(["p2"])
        
        sub_calls = [call[0][0] for call in mock_sub.call_args_list]
        self.assertTrue(any("credential.helper" in " ".join(cmd) and "profile credential-helper" in " ".join(cmd) for cmd in sub_calls))

    @patch('sys.exit', side_effect=SystemExit)
    @patch('sys.stdin')
    @patch('profile.load_profiles')
    def test_handle_credential_helper_get(self, mock_load, mock_stdin, mock_exit):
        mock_load.return_value = {
            "profiles": [
                {"name": "p1", "email": "p1@test.com", "active": True, "git_token": "ghp_realSecretToken123"}
            ]
        }
        mock_stdin.__iter__.return_value = ["protocol=https\n", "host=github.com\n", "\n"]
        
        with patch('builtins.print') as mock_print:
            with self.assertRaises(SystemExit):
                profile.handle_credential_helper(["get"])
                
            printed = [call[0][0] for call in mock_print.call_args_list if call[0]]
            self.assertTrue(any("username=p1@test.com" in p for p in printed))
            self.assertTrue(any("password=ghp_realSecretToken123" in p for p in printed))

    @patch('subprocess.run')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI...")
    @patch('profile.load_profiles')
    @patch('profile.save_profiles')
    def test_handle_add_generate_ssh_success(self, mock_save, mock_load, mock_open, mock_exists, mock_makedirs, mock_sub):
        mock_load.return_value = {"profiles": []}
        
        def exists_side_effect(path):
            if path.endswith(".pub"):
                return True
            return False
        mock_exists.side_effect = exists_side_effect
        mock_sub.return_value = MagicMock(returncode=0)
        
        profile.handle_add(["new-prof", "new@prof.com", "--generate-ssh"])
        
        saved_data = mock_save.call_args[0][0]
        self.assertEqual(len(saved_data["profiles"]), 1)
        self.assertEqual(saved_data["profiles"][0]["name"], "new-prof")
        self.assertTrue(saved_data["profiles"][0]["ssh_key_path"].endswith("id_ed25519_new-prof"))

if __name__ == '__main__':
    unittest.main()
