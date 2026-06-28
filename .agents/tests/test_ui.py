import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
import json

# Inject CLI commands folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import ui

class TestUICommand(unittest.TestCase):

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="## Todo\n- [ ] Task 1 (feat/branch) <!-- id: issue-123 -->\n\n## Doing\n\n## Done\n")
    def test_parse_board_md(self, mock_file, mock_exists):
        mock_exists.return_value = True
        
        data = ui.parse_board_md()
        self.assertIn("todo", data)
        self.assertEqual(len(data["todo"]), 1)
        self.assertEqual(data["todo"][0]["id"], "issue-123")
        self.assertEqual(data["todo"][0]["title"], "Task 1")
        self.assertEqual(data["todo"][0]["branch"], "feat/branch")
        self.assertFalse(data["todo"][0]["completed"])

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="## Todo\n- [ ] Task 1 (feat/branch) <!-- id: issue-123 -->\n\n## Doing\n\n## Done\n")
    def test_update_board_task_status(self, mock_file, mock_exists):
        mock_exists.return_value = True
        
        success = ui.update_board_task_status("issue-123", "doing")
        self.assertTrue(success)
        
        handle = mock_file()
        written_data = "".join(call[0][0] for call in handle.write.call_args_list)
        self.assertIn("## Doing\n  - [ ] Task 1 (feat/branch) <!-- id: issue-123 -->", written_data)
        self.assertNotIn("## Todo\n- [ ] Task 1 (feat/branch) <!-- id: issue-123 -->", written_data)

if __name__ == '__main__':
    unittest.main()
