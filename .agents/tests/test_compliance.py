import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
import json

# Inject scripts folders
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli')))
import validate
import commands.lock as lock

class TestCompliance(unittest.TestCase):

    @patch('subprocess.run')
    def test_get_existing_branches(self, mock_run):
        # Multiple branches returned
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="sha1 refs/heads/feat/issue-023\nsha2 refs/heads/main\n"
        )
        self.assertEqual(lock.get_existing_branches(), {"feat/issue-023", "main"})

        # Git fails (non-zero code)
        mock_run.return_value = MagicMock(returncode=1)
        self.assertEqual(lock.get_existing_branches(), set())

    @patch('commands.lock.get_existing_branches')
    def test_prune_stale_locks(self, mock_get_branches):
        # Setup: lock module 'm1' by b1 (exists) and 'm2' by b2 (stale)
        mock_get_branches.return_value = {"b1"}
        locks = {"m1": "b1", "m2": "b2"}
        pruned = lock.prune_stale_locks(locks)
        self.assertIn("m1", pruned)
        self.assertNotIn("m2", pruned)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"profiles": [{"name": "p1", "email": "p1@corp.com", "active": true}]}')
    @patch('subprocess.run')
    def test_validate_profile_email(self, mock_run, mock_file, mock_exists):
        mock_exists.return_value = True
        
        # Scenario 1: Mismatched Git config email (fails validation)
        def mock_git_calls_mismatch(args, **kwargs):
            if 'diff' in args:
                return MagicMock(returncode=0, stdout="")
            elif 'config' in args:
                return MagicMock(returncode=0, stdout="wrong@personal.com\n")
            return MagicMock(returncode=0)
            
        mock_run.side_effect = mock_git_calls_mismatch
        self.assertFalse(validate.audit_secrets_and_ignored_files())

        # Scenario 2: Matching Git config email (passes validation)
        def mock_git_calls_match(args, **kwargs):
            if 'diff' in args:
                return MagicMock(returncode=0, stdout="")
            elif 'config' in args:
                return MagicMock(returncode=0, stdout="p1@corp.com\n")
            return MagicMock(returncode=0)
            
        mock_run.side_effect = mock_git_calls_match
        self.assertTrue(validate.audit_secrets_and_ignored_files())

if __name__ == '__main__':
    unittest.main()
