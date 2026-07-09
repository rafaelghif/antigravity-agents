import unittest
from unittest.mock import patch, mock_open
import sys
import os

# Inject CLI commands folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import lock

class TestLockCommand(unittest.TestCase):
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_load_locks_empty(self, mock_exists, mock_run):
        mock_exists.return_value = False
        mock_run.return_value = unittest.mock.Mock(returncode=1, stdout="")
        locks = lock.load_locks()
        self.assertEqual(locks, {})

    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_locks_existing(self, mock_file_open, mock_exists, mock_run):
        mock_exists.return_value = True
        mock_res_branch = unittest.mock.Mock()
        mock_res_branch.returncode = 0
        mock_res_branch.stdout = "feat/issue-1\nmain\n"
        
        mock_res_rev = unittest.mock.Mock()
        mock_res_rev.returncode = 0
        mock_res_rev.stdout = "feat/issue-1\n"
        
        mock_run.side_effect = [mock_res_branch, mock_res_rev]
        
        issue_content = """---
status: open
---
- Active module locks:
  - [ ] module-x <!-- id: lock-module_x -->
"""
        mock_file_open.return_value.read.return_value = issue_content
        
        locks = lock.load_locks()
        self.assertEqual(locks.get("module-x"), "feat/issue-1")

    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_locks(self, mock_file_open, mock_exists, mock_run):
        mock_exists.return_value = True
        mock_res_rev = unittest.mock.Mock()
        mock_res_rev.returncode = 0
        mock_res_rev.stdout = "feat/issue-1\n"
        mock_run.return_value = mock_res_rev
        
        current_content = """---
status: open
---
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
"""
        mock_file_open.return_value.read.return_value = current_content
        
        lock.save_locks({"mod-y": "feat/issue-1"})
        
        mock_file_open.return_value.write.assert_called_once()
        written = mock_file_open.return_value.write.call_args[0][0]
        self.assertIn("mod-y", written)

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

    def test_file_lock_mutex_success(self):
        from helper import FileLockMutex
        mutex = FileLockMutex("test_path_dummy", timeout=0.1)
        with patch('os.mkdir') as mock_mkdir, patch('os.rmdir') as mock_rmdir:
            with mutex:
                self.assertTrue(mutex.acquired)
            mock_mkdir.assert_called_once_with("test_path_dummy.lock")
            mock_rmdir.assert_called_once_with("test_path_dummy.lock")
            self.assertFalse(mutex.acquired)

    def test_file_lock_mutex_timeout(self):
        from helper import FileLockMutex
        mutex = FileLockMutex("test_path_dummy", timeout=0.01, delay=0.001)
        with patch('os.mkdir', side_effect=FileExistsError):
            with self.assertRaises(TimeoutError):
                with mutex:
                    pass
            
if __name__ == '__main__':
    unittest.main()

