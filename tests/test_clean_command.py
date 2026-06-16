import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys

# Ensure the cli directory is in the import path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".agents", "scripts", "cli"))
import commands.clean as clean

class TestCleanCommand(unittest.TestCase):
    @patch('shutil.rmtree')
    @patch('os.remove')
    @patch('os.listdir')
    @patch('os.path.isdir')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('subprocess.check_output')
    @patch('utils.get_agents_dir')
    def test_clean_command_execution(self, mock_get_agents_dir, mock_check_output, mock_file_open, mock_exists, mock_isdir, mock_listdir, mock_remove, mock_rmtree):
        mock_get_agents_dir.return_value = "/mock/agents"
        mock_exists.return_value = True
        
        # Mock git branch and commit check_output calls
        mock_check_output.side_effect = [b"main\n", b"abc1234\n"]
        
        # Mock isdir behavior
        def isdir_side_effect(path):
            if "nested_dir" in path or "sprint_main_dir" in path:
                return True
            return False
        mock_isdir.side_effect = isdir_side_effect
        
        # Mock directory contents
        def listdir_side_effect(path):
            if "locks" in path:
                return ["cli.lock", "other.lock", "nested_dir"]
            if "archive" in path:
                return ["sprint_main.md", "sprint_main_dir"]
            if "workflows" in path:
                return ["task_workspace_cleanup_command.md", "task_other.md"]
            return []
            
        mock_listdir.side_effect = listdir_side_effect
        
        # Run clean
        clean.run([])
        
        # Check locks removal
        # other.lock should be removed, nested_dir (directory) should be rmtree'd, cli.lock must NOT be removed
        mock_remove.assert_any_call(os.path.join("/mock/agents", "locks", "other.lock"))
        mock_rmtree.assert_any_call(os.path.join("/mock/agents", "locks", "nested_dir"))
        # Ensure cli.lock is not deleted
        for call_args in mock_remove.call_args_list:
            self.assertNotIn("cli.lock", call_args[0][0])
            
        # Check archive removal
        mock_remove.assert_any_call(os.path.join("/mock/agents", "archive", "sprint_main.md"))
        mock_rmtree.assert_any_call(os.path.join("/mock/agents", "archive", "sprint_main_dir"))
        
        # Check workflows removal
        mock_remove.assert_any_call(os.path.join("/mock/agents", "workflows", "task_other.md"))
        # Ensure task_workspace_cleanup_command.md is not deleted
        for call_args in mock_remove.call_args_list:
            self.assertNotIn("task_workspace_cleanup_command.md", call_args[0][0])
            
        # Verify default budget was written
        # Verify active profile reset and keys templates written
        self.assertTrue(mock_file_open.called)
        
        # Check that memory.md was written with git info
        # Find memory.md open call
        memory_written = False
        for call in mock_file_open.call_args_list:
            if "memory.md" in call[0][0]:
                memory_written = True
                break
        self.assertTrue(memory_written)

if __name__ == '__main__':
    unittest.main()
