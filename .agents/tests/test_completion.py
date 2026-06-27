import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import completion

def raise_system_exit(code=0):
    raise SystemExit(code)

class TestCompletionCommand(unittest.TestCase):

    @patch('sys.exit', side_effect=raise_system_exit)
    @patch('builtins.print')
    def test_completion_bash(self, mock_print, mock_exit):
        with self.assertRaises(SystemExit) as cm:
            completion.run(["bash"])
        self.assertEqual(cm.exception.code, 0)
        printed = mock_print.call_args[0][0]
        self.assertIn("compgen", printed)
        self.assertIn("complete -F _aac_completion aac", printed)

    @patch('sys.exit', side_effect=raise_system_exit)
    @patch('builtins.print')
    def test_completion_zsh(self, mock_print, mock_exit):
        with self.assertRaises(SystemExit) as cm:
            completion.run(["zsh"])
        self.assertEqual(cm.exception.code, 0)
        printed = mock_print.call_args[0][0]
        self.assertIn("_arguments", printed)
        self.assertIn("#compdef aac helper.sh", printed)

    @patch('sys.exit', side_effect=raise_system_exit)
    def test_completion_invalid(self, mock_exit):
        with self.assertRaises(SystemExit) as cm:
            completion.run(["fish"])
        self.assertEqual(cm.exception.code, 1)

if __name__ == '__main__':
    unittest.main()
