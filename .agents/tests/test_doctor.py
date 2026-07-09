import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import doctor

def raise_system_exit(code=0):
    raise SystemExit(code)

class TestDoctorCommand(unittest.TestCase):

    @patch('sys.exit', side_effect=raise_system_exit)
    @patch('doctor.check_python', return_value=True)
    @patch('doctor.check_git', return_value=True)
    @patch('doctor.check_worktree', return_value=True)
    @patch('doctor.check_identity', return_value=True)
    @patch('doctor.check_profiles', return_value=True)
    @patch('doctor.check_network', return_value=True)
    def test_doctor_run_success(self, mock_net, mock_prof, mock_ident, mock_work, mock_git, mock_py, mock_exit):
        with self.assertRaises(SystemExit) as cm:
            doctor.run([])
        self.assertEqual(cm.exception.code, 0)

    @patch('sys.exit', side_effect=raise_system_exit)
    @patch('doctor.check_python', return_value=True)
    @patch('doctor.check_git', return_value=False)
    @patch('doctor.check_worktree', return_value=True)
    @patch('doctor.check_identity', return_value=True)
    @patch('doctor.check_profiles', return_value=True)
    @patch('doctor.check_network', return_value=True)
    def test_doctor_run_failure(self, mock_net, mock_prof, mock_ident, mock_work, mock_git, mock_py, mock_exit):
        with self.assertRaises(SystemExit) as cm:
            doctor.run([])
        self.assertEqual(cm.exception.code, 1)

    @patch('doctor.perform_repairs')
    @patch('sys.exit', side_effect=raise_system_exit)
    @patch('doctor.check_python', return_value=True)
    @patch('doctor.check_git', return_value=True)
    @patch('doctor.check_worktree', return_value=True)
    @patch('doctor.check_identity', return_value=True)
    @patch('doctor.check_profiles', return_value=True)
    @patch('doctor.check_network', return_value=True)
    def test_doctor_run_repair_mode(self, mock_net, mock_prof, mock_ident, mock_work, mock_git, mock_py, mock_exit, mock_repair):
        with self.assertRaises(SystemExit) as cm:
            doctor.run(["--repair"])
        self.assertEqual(cm.exception.code, 0)
        mock_repair.assert_called_once()

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('shutil.copy')
    @patch('subprocess.run')
    def test_perform_repairs(self, mock_run, mock_copy, mock_makedirs, mock_open_file, mock_exists):
        # mock exists to return True for example profile and git directory checks, False for others
        mock_exists.side_effect = lambda path: True if "example" in path or "hooks" in path or path.endswith(".git") or path.endswith("git-dir") else False
        mock_run.return_value = MagicMock(returncode=0, stdout="refs/heads/main\n")
        
        doctor.perform_repairs()
        
        # Verify it tries to create/write missing config files
        mock_open_file.assert_any_call(".agents/state/locks.json", "w", encoding="utf-8")
        mock_open_file.assert_any_call(".agents/state/token_budget.json", "w", encoding="utf-8")
        mock_open_file.assert_any_call(".agents/projects.json", "w", encoding="utf-8")
        
        # Verify it tries to copy profiles file
        mock_copy.assert_called_once_with(".agents/git_profiles.example", ".agents/git_profiles.json")

if __name__ == '__main__':
    unittest.main()
