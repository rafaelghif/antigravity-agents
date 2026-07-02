import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import tempfile
import shutil

# Inject scripts folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
import recon

class TestReconCommand(unittest.TestCase):
    def setUp(self):
        self.old_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        
    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.temp_dir)

    def test_scan_workspace_python(self):
        # Create dummy Python project setup
        with open("requirements.txt", 'w', encoding='utf-8') as f:
            f.write("pytest\nflake8\n")
        with open("main.py", 'w', encoding='utf-8') as f:
            f.write("print('hello')\n")
            
        results = recon.scan_workspace()
        self.assertEqual(results["main_stack"], "python")
        self.assertIn("Python 3", results["stack"])

    def test_scan_workspace_node(self):
        # Create dummy Node project setup
        with open("package.json", 'w', encoding='utf-8') as f:
            f.write('{"name": "test"}')
            
        results = recon.scan_workspace()
        self.assertEqual(results["main_stack"], "node")
        self.assertIn("Node.js", results["stack"])

    def test_generate_recommendations_report(self):
        # 1. Dummy Python scan results, but directories 'src' and 'tests' are missing.
        scan_results = {
            "stack": "Python 3",
            "main_stack": "python",
            "test_command": "pytest"
        }
        
        # Run report generation
        recon.generate_recommendations_report(scan_results)
        
        report_path = ".agents/plans/recon_recommendations.md"
        self.assertTrue(os.path.exists(report_path))
        
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Verify missing directories are identified
            self.assertIn("src/` directory is missing", content)
            self.assertIn("tests/` directory is missing", content)
            # Verify missing dependencies are listed (requirements.txt doesn't exist yet)
            self.assertIn("pytest` is not installed", content)
            self.assertIn("flake8` is not installed", content)

if __name__ == '__main__':
    unittest.main()
