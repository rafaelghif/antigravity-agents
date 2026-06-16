import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure the cli directory is in the import path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".agents", "scripts", "cli"))
import commands.menu as menu

class TestMenuCommand(unittest.TestCase):
    @patch('sys.stdout.isatty', return_value=False)
    @patch('commands.menu.get_git_info')
    @patch('commands.menu.get_active_api_profile')
    @patch('commands.menu.get_active_locks')
    @patch('commands.menu.run_subcommand')
    @patch('builtins.input')
    def test_menu_exit(self, mock_input, mock_run_subcommand, mock_get_active_locks, mock_get_active_api_profile, mock_get_git_info, mock_isatty):
        # Setup mocks
        mock_get_git_info.return_value = ("main", "user@example.com")
        mock_get_active_api_profile.return_value = "work"
        mock_get_active_locks.return_value = ["cli"]
        
        # input returns '0' to exit
        mock_input.return_value = "0"
        
        menu.run([])
        
        # Verify exit input was requested and no subcommands were called
        mock_input.assert_called_once_with("Select choice [0-13]: ")
        mock_run_subcommand.assert_not_called()

    @patch('sys.stdout.isatty', return_value=False)
    @patch('commands.menu.get_git_info')
    @patch('commands.menu.get_active_api_profile')
    @patch('commands.menu.get_active_locks')
    @patch('commands.menu.run_subcommand')
    @patch('builtins.input')
    def test_menu_doctor_then_exit(self, mock_input, mock_run_subcommand, mock_get_active_locks, mock_get_active_api_profile, mock_get_git_info, mock_isatty):
        mock_get_git_info.return_value = ("main", "user@example.com")
        mock_get_active_api_profile.return_value = "work"
        mock_get_active_locks.return_value = []
        
        # first input is '5' (doctor), second input is for the "Press Enter" prompt, third input is '0' (exit)
        mock_input.side_effect = ["5", "", "0"]
        
        menu.run([])
        
        # doctor should be called
        mock_run_subcommand.assert_any_call("doctor")

    @patch('sys.stdout.isatty', return_value=False)
    @patch('commands.menu.get_git_info')
    @patch('commands.menu.get_active_api_profile')
    @patch('commands.menu.get_active_locks')
    @patch('commands.menu.run_subcommand')
    @patch('builtins.input')
    def test_menu_lock_unlock(self, mock_input, mock_run_subcommand, mock_get_active_locks, mock_get_active_api_profile, mock_get_git_info, mock_isatty):
        mock_get_git_info.return_value = ("main", "user@example.com")
        mock_get_active_api_profile.return_value = "work"
        mock_get_active_locks.side_effect = [
            [],        # cycle 1 start
            ["core"],  # cycle 2 start
            ["core"],  # inside choice == "2" scan
            ["core"],  # cycle 3 start
            ["core"]   # fallback
        ]
        
        # 1. Option '1' -> lock 'core'
        # 2. Option '2' -> unlock choice '1' (core)
        # 3. Option '0' -> exit
        mock_input.side_effect = ["1", "core", "2", "1", "0"]
        
        menu.run([])
        
        mock_run_subcommand.assert_any_call("lock", ["core"])
        mock_run_subcommand.assert_any_call("unlock", ["core"])

if __name__ == '__main__':
    unittest.main()
