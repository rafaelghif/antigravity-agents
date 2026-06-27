import unittest
from unittest.mock import patch, MagicMock
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

if __name__ == '__main__':
    unittest.main()
