import unittest
import subprocess
import os
import sys

# Import the module directly to test its internal logic
sys.path.append(os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".agents", "skills", "pr-scaffolder", "scripts"
))
import main

class TestSkillPrScaffolder(unittest.TestCase):
    def test_help_execution(self):
        """Verify that the skill script can be executed with --help."""
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            ".agents", "skills", "pr-scaffolder", "scripts", "main.py"
        )
        self.assertTrue(os.path.exists(script_path), f"Script not found at {script_path}")
        
        proc = subprocess.run([script_path, "--help"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("PR review guide generator", proc.stdout)

    def test_extract_symbol_python(self):
        """Verify symbol extraction for Python definitions."""
        self.assertEqual(main.extract_symbol("+def hello_world():"), "def hello_world")
        self.assertEqual(main.extract_symbol("+    class MyContainer:"), "class MyContainer")
        self.assertIsNone(main.extract_symbol("+# Some comment"))
        self.assertIsNone(main.extract_symbol("+x = 5"))

    def test_extract_symbol_go(self):
        """Verify symbol extraction for Go functions and types."""
        self.assertEqual(main.extract_symbol("+func (c *Client) FetchData(ctx context.Context) error"), "func FetchData")
        self.assertEqual(main.extract_symbol("+func SimpleFunc()"), "func SimpleFunc")
        self.assertEqual(main.extract_symbol("+type User struct {"), "type User")

    def test_extract_symbol_javascript(self):
        """Verify symbol extraction for Javascript/Typescript definitions."""
        self.assertEqual(main.extract_symbol("+function calculateTotal(items) {"), "function calculateTotal")
        self.assertEqual(main.extract_symbol("+interface Product {"), "interface Product")

    def test_report_generation(self):
        """Verify report markdown formatting."""
        report = main.generate_report(
            workspace_root="/tmp",
            current_branch="feature/test",
            base_branch="main",
            changed_files=["file1.py"],
            test_cmd="echo 'test runner'",
            test_logs="test output log\npassed",
            test_failed=False,
            test_skipped=False,
            schema_diff="Some schema changes"
        )
        self.assertIn("# PR Review Guide: feature/test", report)
        self.assertIn("## 1. Scope of Work", report)
        self.assertIn("## 2. Verification Logs", report)
        self.assertIn("## 3. Schema Changes", report)
        self.assertIn("test output log", report)
        self.assertIn("Some schema changes", report)
        self.assertIn("> [!NOTE]\n> Verification tests passed successfully.", report)

if __name__ == '__main__':
    unittest.main()
