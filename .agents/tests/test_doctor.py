import unittest
from unittest.mock import patch, MagicMock
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
    @patch('doctor.handle_fixes')
    def test_doctor_run_failure(self, mock_fix, mock_net, mock_prof, mock_ident, mock_work, mock_git, mock_py, mock_exit):
        with self.assertRaises(SystemExit) as cm:
            doctor.run([])
        self.assertEqual(cm.exception.code, 1)
        mock_fix.assert_called_once()

if __name__ == '__main__':
    unittest.main()
