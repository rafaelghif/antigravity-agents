import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import context

def raise_system_exit(code=0):
    raise SystemExit(code)

class TestContextCommand(unittest.TestCase):

    @patch('sys.exit', side_effect=raise_system_exit)
    @patch('context.get_current_branch', return_value="feat/issue-123")
    @patch('context.get_issue_details')
    @patch('context.get_locked_modules', return_value=["validate"])
    @patch('context.get_git_changes', return_value=["M helper.py"])
    @patch('builtins.open', new_callable=mock_open)
    def test_context_run_success(self, mock_file, mock_changes, mock_locks, mock_details, mock_branch, mock_exit):
        mock_details.return_value = {
            "title": "Test Issue",
            "tasks": ["- [ ] Task 1"],
            "description": "Test Desc"
        }
        
        with self.assertRaises(SystemExit) as cm:
            context.run(["optimize"])
            
        self.assertEqual(cm.exception.code, 0)
        mock_file.assert_any_call(".agents/rules.md", 'r', encoding='utf-8')
        mock_file.assert_any_call(".agents/state/active_context.md", 'w', encoding='utf-8')

    @patch('sys.exit', side_effect=raise_system_exit)
    def test_context_run_invalid_args(self, mock_exit):
        with self.assertRaises(SystemExit) as cm:
            context.run([])
        self.assertEqual(cm.exception.code, 1)

    @patch('os.path.exists')
    @patch('builtins.open')
    def test_get_workflow_mode(self, mock_open_file, mock_exists):
        mock_exists.return_value = True
        mock_open_file.return_value = io.StringIO('{"workflow_mode": "solo"}')
        self.assertEqual(context.get_workflow_mode(), "solo")

        mock_open_file.return_value = io.StringIO('{"workflow_mode": "team"}')
        self.assertEqual(context.get_workflow_mode(), "team")

        mock_exists.return_value = False
        self.assertEqual(context.get_workflow_mode(), "team")

    @patch('sys.exit', side_effect=raise_system_exit)
    @patch('context.get_workflow_mode', return_value="solo")
    @patch('context.get_current_branch', return_value="main")
    @patch('context.get_issue_details')
    @patch('context.get_locked_modules', return_value=[])
    @patch('context.get_git_changes', return_value=[])
    @patch('builtins.open', new_callable=mock_open)
    def test_context_run_solo(self, mock_file, mock_changes, mock_locks, mock_details, mock_branch, mock_mode, mock_exit):
        mock_details.return_value = {
            "title": "Unknown Title",
            "tasks": [],
            "description": "No description found."
        }
        
        with self.assertRaises(SystemExit) as cm:
            context.run(["optimize"])
            
        self.assertEqual(cm.exception.code, 0)
        mock_file.assert_any_call(".agents/state/active_context.md", 'w', encoding='utf-8')

if __name__ == '__main__':
    unittest.main()
