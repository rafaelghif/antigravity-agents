import unittest
from unittest.mock import patch, mock_open, MagicMock
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
            mock_file.assert_called_with(".agents/memory/lessons-learned.md", 'w', encoding='utf-8')
            
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data="")
    def test_learn_bootstrap_file(self, mock_file, mock_makedirs, mock_exists):
        mock_exists.return_value = False
        with patch('builtins.print') as mock_print:
            learn.run(["Limit subagent spawns"])
            mock_print.assert_called_once()

    @patch('subprocess.run')
    def test_analyze_diff_mock_match(self, mock_run):
        # Configure subprocess mocks for git diff name-only and git diff patch
        mock_files = MagicMock(returncode=0, stdout="test_cli.py\nsrc/model.py\n")
        mock_diff = MagicMock(returncode=0, stdout="diff --git a/test_cli.py b/test_cli.py\n+mock.patch('sys.exit')\n")
        mock_run.side_effect = [mock_diff, mock_files]
        
        suggestions = learn.analyze_diff("main")
        self.assertTrue(len(suggestions) > 0)
        categories = [s[0] for s in suggestions]
        self.assertIn("Testing / Mocking", categories)

    @patch('subprocess.run')
    def test_analyze_diff_skill_evolution_match(self, mock_run):
        mock_files = MagicMock(returncode=0, stdout=".agents/skills/my-skill/SKILL.md\n")
        mock_diff = MagicMock(returncode=0, stdout="diff --git a/SKILL.md b/SKILL.md\n+name: my-skill\n+description: my scaffold description\n")
        mock_run.side_effect = [mock_diff, mock_files]
        
        suggestions = learn.analyze_diff("main")
        self.assertTrue(len(suggestions) > 0)
        categories = [s[0] for s in suggestions]
        self.assertIn("Skill Evolution / Self-Improvement", categories)

    @patch('sys.stdin.isatty', return_value=True)
    @patch('builtins.input', side_effect=['1'])
    @patch('learn.analyze_diff', return_value=[("Testing / Mocking", "Ensure mock side effects are isolated.")])
    @patch('learn.record_lesson')
    def test_suggest_and_record_lessons_select(self, mock_record, mock_analyze, mock_input, mock_isatty):
        learn.suggest_and_record_lessons("main")
        mock_record.assert_called_once_with("Ensure mock side effects are isolated.", "Testing / Mocking")

    @patch('sys.stdin.isatty', return_value=True)
    @patch('builtins.input', side_effect=['2', 'My custom lesson', 'General'])
    @patch('learn.analyze_diff', return_value=[("Testing / Mocking", "Ensure mock side effects are isolated.")])
    @patch('learn.record_lesson')
    def test_suggest_and_record_lessons_custom(self, mock_record, mock_analyze, mock_input, mock_isatty):
        # Options: 1. Testing/Mocking, 2. Custom, 3. Skip
        learn.suggest_and_record_lessons("main")
        mock_record.assert_called_once_with("My custom lesson", "General")

    @patch('sys.stdin.isatty', return_value=True)
    @patch('builtins.input', side_effect=['3'])
    @patch('learn.analyze_diff', return_value=[("Testing / Mocking", "Ensure mock side effects are isolated.")])
    @patch('learn.record_lesson')
    def test_suggest_and_record_lessons_skip(self, mock_record, mock_analyze, mock_input, mock_isatty):
        # Options: 1. Testing/Mocking, 2. Custom, 3. Skip
        learn.suggest_and_record_lessons("main")
        mock_record.assert_not_called()

    @patch('sys.stdin.isatty', return_value=False)
    @patch('learn.analyze_diff', return_value=[("Testing / Mocking", "Ensure mock side effects are isolated.")])
    @patch('learn.extract_lessons_from_commits', return_value=[("Git Commit", "Commit lesson")])
    @patch('learn.record_lesson')
    def test_suggest_and_record_lessons_non_interactive(self, mock_record, mock_extract, mock_analyze, mock_isatty):
        learn.suggest_and_record_lessons("main")
        mock_analyze.assert_called_once_with("main")
        mock_extract.assert_called_once_with("main")
        mock_record.assert_any_call("Ensure mock side effects are isolated.", "Testing / Mocking")
        mock_record.assert_any_call("Commit lesson", "Git Commit")

    @patch('learn.suggest_and_record_lessons')
    @patch('subprocess.run')
    def test_run_from_diff(self, mock_run, mock_suggest):
        mock_run.return_value = MagicMock(returncode=0)
        learn.run(["--from-diff"])
        mock_suggest.assert_called_once()

if __name__ == '__main__':
    unittest.main()
