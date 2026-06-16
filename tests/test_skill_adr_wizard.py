import unittest
import subprocess
import os
import sys
import json

class TestSkillAdrWizard(unittest.TestCase):
    def setUp(self):
        self.workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.script_path = os.path.join(
            self.workspace_root, ".agents", "skills", "adr-wizard", "scripts", "main.py"
        )
        self.adr_index_path = os.path.join(self.workspace_root, ".agents", "adr.md")
        
        # Backup adr.md
        self.index_backup = None
        if os.path.exists(self.adr_index_path):
            with open(self.adr_index_path, "r", encoding="utf-8") as f:
                self.index_backup = f.read()

    def tearDown(self):
        # Restore adr.md
        if self.index_backup is not None:
            with open(self.adr_index_path, "w", encoding="utf-8") as f:
                f.write(self.index_backup)

    def test_help_execution(self):
        """Verify that the skill script can be executed with --help."""
        self.assertTrue(os.path.exists(self.script_path), f"Script not found at {self.script_path}")
        
        proc = subprocess.run([sys.executable, self.script_path, "--help"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("guided wizard", proc.stdout)

    def test_non_interactive_generation(self):
        """Verify non-interactive generation of ADR files."""
        title = "Test ADR from Automated Unit Test"
        status = "proposed"
        context = "Test Context Description"
        decision = "Test Decision Description"
        consequences = "Test Consequences Description"
        
        proc = subprocess.run([
            sys.executable, self.script_path,
            "--title", title,
            "--status", status,
            "--context", context,
            "--decision", decision,
            "--consequences", consequences
        ], capture_output=True, text=True)
        
        self.assertEqual(proc.returncode, 0)
        res = json.loads(proc.stdout)
        self.assertEqual(res["status"], "success")
        
        filename = res["data"]["filename"]
        self.assertTrue(os.path.exists(filename))
        
        # Verify content of the generated file
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Test Context Description", content)
            self.assertIn("Test Decision Description", content)
            self.assertIn("Test Consequences Description", content)
            
        # Clean up the created file
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    unittest.main()
