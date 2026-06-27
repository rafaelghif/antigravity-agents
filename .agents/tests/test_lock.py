import unittest
from unittest.mock import patch, mock_open
import sys
import os

# Inject CLI commands folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import lock

class TestLockCommand(unittest.TestCase):
    @patch('os.path.exists')
    def test_load_locks_empty(self, mock_exists):
        mock_exists.return_value = False
        locks = lock.load_locks()
        self.assertEqual(locks, {})

    @patch('lock.branch_exists')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"module-x": "feat/issue-1"}')
    def test_load_locks_existing(self, mock_file, mock_exists, mock_branch):
        mock_exists.return_value = True
        mock_branch.return_value = True
        locks = lock.load_locks()
        self.assertEqual(locks.get("module-x"), "feat/issue-1")

    @patch('builtins.open', new_callable=mock_open)
    def test_save_locks(self, mock_file):
        lock.save_locks({"mod-y": "some-branch"})
        mock_file.assert_called_once_with(lock.LOCK_FILE, 'w', encoding='utf-8')

    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{}')
    def test_acquire_lock_success(self, mock_file, mock_exists, mock_sub):
        mock_exists.return_value = True
        # Mock git branch call
        mock_res = unittest.mock.Mock()
        mock_res.stdout = "feat/test-branch\n"
        mock_sub.return_value = mock_res
        
        with patch('lock.save_locks') as mock_save:
            lock.run(["module-to-lock"])
            mock_save.assert_called_once()
            
if __name__ == '__main__':
    unittest.main()
