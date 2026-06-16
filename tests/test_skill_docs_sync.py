import unittest
import subprocess
import os
import sys
import tempfile
import shutil

class TestSkillDocsSync(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        self.script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            ".agents", "skills", "docs-sync", "scripts", "main.py"
        )

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)

    def test_help_execution(self):
        """Verify that the skill script can be executed with --help."""
        self.assertTrue(os.path.exists(self.script_path), f"Script not found at {self.script_path}")
        
        proc = subprocess.run([sys.executable, self.script_path, "--help"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Synchronize Python docstrings with Markdown", proc.stdout)

    def test_docstring_sync_execution(self):
        """Verify that docstrings are parsed and successfully synced into target markdown."""
        
        # 1. Create mock Python source file
        py_content = '''"""
This is a mock module level docstring.
It has multiple lines.
"""

class MockCalculator:
    """
    Mock class for mathematical operations.
    """
    def add(self, a: int, b: int = 0) -> int:
        """
        Adds two numbers together.
        """
        return a + b

def mock_helper_function(message: str) -> None:
    """
    Helper function that prints a message.
    """
    print(message)
'''
        src_path = os.path.join(self.test_dir, "mock_source.py")
        with open(src_path, "w", encoding="utf-8") as f:
            f.write(py_content)
            
        # 2. Create mock Markdown file with placeholders
        md_content = f'''# Project Documentation

Before the docs.

<!-- DOCS-SYNC:START({src_path}) -->
OLD CONTENT THAT SHOULD BE OVERWRITTEN
<!-- DOCS-SYNC:END({src_path}) -->

After the docs.
'''
        target_path = os.path.join(self.test_dir, "docs.md")
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        # 3. Run the docs-sync script specifying both source and target
        proc = subprocess.run(
            [sys.executable, self.script_path, "--target", target_path, "--source", src_path],
            capture_output=True,
            text=True
        )
        self.assertEqual(proc.returncode, 0, f"Script failed with stderr: {proc.stderr}")
        
        # 4. Verify output content
        with open(target_path, "r", encoding="utf-8") as f:
            updated_content = f.read()
            
        self.assertIn("### Module Reference: `mock_source.py`", updated_content)
        self.assertIn("> This is a mock module level docstring.", updated_content)
        
        self.assertIn("#### Class: `MockCalculator`", updated_content)
        self.assertIn("> Mock class for mathematical operations.", updated_content)
        
        self.assertIn("##### Method: `MockCalculator.add`", updated_content)
        self.assertIn("def add(self, a: int, b: int=0) -> int", updated_content)
        self.assertIn("> Adds two numbers together.", updated_content)
        
        self.assertIn("##### Function: `mock_helper_function`", updated_content)
        self.assertIn("def mock_helper_function(message: str) -> None", updated_content)
        self.assertIn("> Helper function that prints a message.", updated_content)
        
        # Verify placeholders still remain intact
        self.assertIn(f"<!-- DOCS-SYNC:START({src_path}) -->", updated_content)
        self.assertIn(f"<!-- DOCS-SYNC:END({src_path}) -->", updated_content)

    def test_autodetect_mode(self):
        """Verify that omitting --source scans the target markdown for placeholders automatically."""
        # 1. Create mock Python source file
        py_content = '''"""
Autodetect test module docstring.
"""
def test_func():
    """
    Test function docstring.
    """
    pass
'''
        src_path = os.path.join(self.test_dir, "auto_source.py")
        with open(src_path, "w", encoding="utf-8") as f:
            f.write(py_content)
            
        # 2. Create mock Markdown file with placeholders containing the source path
        md_content = f'''# Auto-detect Test

<!-- DOCS-SYNC:START({src_path}) -->
<!-- DOCS-SYNC:END({src_path}) -->
'''
        target_path = os.path.join(self.test_dir, "auto_docs.md")
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        # 3. Run the docs-sync script without specifying --source
        proc = subprocess.run(
            [sys.executable, self.script_path, "--target", target_path],
            capture_output=True,
            text=True
        )
        self.assertEqual(proc.returncode, 0, f"Script failed with stderr: {proc.stderr}")
        
        # 4. Verify output content
        with open(target_path, "r", encoding="utf-8") as f:
            updated_content = f.read()
            
        self.assertIn("### Module Reference: `auto_source.py`", updated_content)
        self.assertIn("> Autodetect test module docstring.", updated_content)
        self.assertIn("##### Function: `test_func`", updated_content)
        self.assertIn("> Test function docstring.", updated_content)

if __name__ == '__main__':
    unittest.main()
