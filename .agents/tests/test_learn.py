import unittest
from unittest.mock import patch, mock_open
import sys
import os

# Inject CLI commands folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import learn

class TestLearnCommand(unittest.TestCase):
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data="# AAC V2 Lessons Learned\n\n## Lessons Learned\n")
    def test_learn_append(self, mock_file, mock_makedirs, mock_exists):
        mock_exists.return_value = True
        with patch('builtins.print') as mock_print:
            learn.run(["Always limit file reads", "--category", "Performance"])
            mock_print.assert_called_once()
            
            # Assert file write happened
            mock_file.assert_called_with(".agents/memory/lessons-learned.md", 'w', encoding='utf-8')
            
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data="")
    def test_learn_bootstrap_file(self, mock_file, mock_makedirs, mock_exists):
        mock_exists.return_value = False
        with patch('builtins.print') as mock_print:
            learn.run(["Limit subagent spawns"])
            mock_print.assert_called_once()
            
if __name__ == '__main__':
    unittest.main()
