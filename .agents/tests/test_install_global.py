import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import install_global

def raise_system_exit(code=0):
    raise SystemExit(code)

class TestInstallGlobalCommand(unittest.TestCase):

    @patch('sys.exit', side_effect=raise_system_exit)
    @patch('os.makedirs')
    @patch('os.stat')
    @patch('os.chmod')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.environ.get', return_value="/usr/bin:/bin")
    def test_install_global_unix(self, mock_env, mock_file, mock_chmod, mock_stat, mock_makedirs, mock_exit):
        with patch('os.name', 'posix'):
            with self.assertRaises(SystemExit) as cm:
                install_global.run([])
            self.assertEqual(cm.exception.code, 0)
            mock_file.assert_called_once()
            self.assertEqual(mock_file.call_args[0][1], 'w')

    @patch('sys.exit', side_effect=raise_system_exit)
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.environ.get', return_value="C:\\Windows\\system32")
    def test_install_global_windows(self, mock_env, mock_file, mock_makedirs, mock_exit):
        with patch('os.name', 'nt'):
            with self.assertRaises(SystemExit) as cm:
                install_global.run([])
            self.assertEqual(cm.exception.code, 0)
            mock_file.assert_called_once()
            self.assertTrue(mock_file.call_args[0][0].endswith("aac.ps1"))

if __name__ == '__main__':
    unittest.main()
