import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli')))
import commands.skill as skill

class TestSkillCommand(unittest.TestCase):

    @patch('os.path.isdir')
    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('commands.skill.parse_skill_desc')
    def test_handle_list(self, mock_desc, mock_listdir, mock_exists, mock_isdir):
        mock_isdir.return_value = True
        mock_exists.return_value = True
        mock_listdir.return_value = ["skill-a", "skill-b"]
        mock_desc.side_effect = ["Desc A", "Desc B"]
        
        with patch('builtins.print') as mock_print:
            skill.handle_list()
            printed = [call[0][0] for call in mock_print.call_args_list]
            self.assertTrue(any("skill-a" in p for p in printed))
            self.assertTrue(any("skill-b" in p for p in printed))

    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('shutil.copytree')
    @patch('shutil.rmtree')
    @patch('commands.skill.run_sync')
    def test_handle_install_local_success(self, mock_sync, mock_rm, mock_copy, mock_exists, mock_makedirs):
        def exists_side_effect(path):
            if path.endswith("SKILL.md"):
                return True
            return True
        mock_exists.side_effect = exists_side_effect
        
        skill.handle_install("local/path/to/skill-c")
        
        mock_copy.assert_called_once()
        mock_sync.assert_called_once()

    @patch('os.path.exists')
    @patch('shutil.rmtree')
    @patch('commands.skill.run_sync')
    def test_handle_uninstall_success(self, mock_sync, mock_rm, mock_exists):
        mock_exists.return_value = True
        
        skill.handle_uninstall("skill-c")
        
        mock_rm.assert_called_with(os.path.join(".agents/skills", "skill-c"))
        mock_sync.assert_called_once()

if __name__ == '__main__':
    unittest.main()
