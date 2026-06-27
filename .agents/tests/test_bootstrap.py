import unittest
import tempfile
import shutil
import os
import sys

# Inject CLI commands folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import bootstrap

from unittest.mock import patch

@patch('builtins.input', return_value='n')
class TestBootstrapCommand(unittest.TestCase):
    
    def setUp(self):
        self.old_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        
    def tearDown(self):
        os.chdir(self.old_cwd)
        # Force clean file handles if any
        shutil.rmtree(self.temp_dir)

    def test_bootstrap_clean_python(self, mock_input):
        # Run bootstrap command
        # args: <name> <stack> <arch>
        bootstrap.run(["TestPythonClean", "python", "clean"])
        
        # Verify clean python folders
        expected_dirs = [
            "src/core/entities",
            "src/core/usecases",
            "src/infrastructure/database",
            "src/infrastructure/repositories",
            "src/presentation/api",
            "src/presentation/cli",
            "tests/unit",
            "tests/integration"
        ]
        for d in expected_dirs:
            self.assertTrue(os.path.isdir(os.path.join(self.temp_dir, d)))
            self.assertTrue(os.path.exists(os.path.join(self.temp_dir, d, "__init__.py")))

        # Verify stack config files
        self.assertTrue(os.path.exists("requirements.txt"))
        with open("requirements.txt", 'r') as f:
            content = f.read()
            self.assertIn("pytest", content)
            self.assertIn("flake8", content)

        # Verify schema.md
        self.assertTrue(os.path.exists(".agents/schema.md"))
        with open(".agents/schema.md", 'r') as f:
            schema = f.read()
            self.assertIn("TestPythonClean", schema)
            self.assertIn("Python", schema)
            self.assertIn("CLEAN Architecture", schema)

        # Verify AGENTS.md
        self.assertTrue(os.path.exists("AGENTS.md"))
        with open("AGENTS.md", 'r') as f:
            agents = f.read()
            self.assertIn("TestPythonClean", agents)

    def test_bootstrap_layered_node(self, mock_input):
        bootstrap.run(["TestNodeLayered", "node", "layered"])
        
        # Verify layered folders
        expected_dirs = [
            "src/api",
            "src/services",
            "src/repositories",
            "src/models",
            "tests"
        ]
        for d in expected_dirs:
            self.assertTrue(os.path.isdir(os.path.join(self.temp_dir, d)))

        # Verify package.json
        self.assertTrue(os.path.exists("package.json"))
        with open("package.json", 'r') as f:
            content = f.read()
            self.assertIn("testnodelayered", content.replace("_", "").replace("-", ""))

    def test_bootstrap_mvc_php(self, mock_input):
        bootstrap.run(["TestPhpMvc", "php", "mvc"])
        
        # Verify MVC folders
        expected_dirs = [
            "src/models",
            "src/views",
            "src/controllers",
            "tests"
        ]
        for d in expected_dirs:
            self.assertTrue(os.path.isdir(os.path.join(self.temp_dir, d)))

        # Verify composer.json
        self.assertTrue(os.path.exists("composer.json"))
        with open("composer.json", 'r') as f:
            content = f.read()
            self.assertIn("phpunit", content)

    def test_bootstrap_invalid_args(self, mock_input):
        # Invalid stack
        with self.assertRaises(SystemExit):
            bootstrap.run(["TestInvalid", "ruby", "clean"])

        # Invalid architecture
        with self.assertRaises(SystemExit):
            bootstrap.run(["TestInvalid", "python", "monolith"])

    @patch('os.path.exists')
    def test_bootstrap_agents_md_fallback(self, mock_exists, mock_input):
        # Mock exists to return False for source AGENTS.md but handle other checks
        from genericpath import exists as real_exists
        mock_exists.side_effect = lambda path: False if "AGENTS.md" in path and ("scripts" in path or ".." in path) else real_exists(path)
        
        bootstrap.run(["FallbackProject", "python", "clean"])
        self.assertTrue(os.path.exists("AGENTS.md"))
        with open("AGENTS.md", 'r') as f:
            content = f.read()
            self.assertIn("FallbackProject", content)
            self.assertIn("Python (CLEAN)", content)

if __name__ == '__main__':
    unittest.main()
