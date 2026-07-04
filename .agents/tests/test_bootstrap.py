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
        with open("requirements.txt", 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("pytest", content)
            self.assertIn("flake8", content)

        # Verify schema.md
        self.assertTrue(os.path.exists(".agents/schema.md"))
        with open(".agents/schema.md", 'r', encoding='utf-8') as f:
            schema = f.read()
            self.assertIn("TestPythonClean", schema)
            self.assertIn("Python", schema)
            self.assertIn("CLEAN Architecture", schema)

        # Verify AGENTS.md
        self.assertTrue(os.path.exists("AGENTS.md"))
        with open("AGENTS.md", 'r', encoding='utf-8') as f:
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
        with open("package.json", 'r', encoding='utf-8') as f:
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
        with open("composer.json", 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("phpunit", content)

    def test_bootstrap_invalid_args(self, mock_input):
        # Empty stack name
        with self.assertRaises(SystemExit):
            bootstrap.run(["TestInvalid", "", "clean"])

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
        with open("AGENTS.md", 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("FallbackProject", content)
            self.assertIn("Python (CLEAN)", content)

    def test_read_template(self, mock_input):
        src_root = os.path.abspath(os.path.join(os.path.dirname(bootstrap.__file__), "../../../../"))
        
        # Verify python_requirements.txt template reads correctly
        req_template = bootstrap.read_template(src_root, "python_requirements.txt.template")
        self.assertIn("pytest", req_template)
        
        # Verify fallback for missing file
        missing_template = bootstrap.read_template(src_root, "non_existent.template", "fallback_content")
        self.assertEqual(missing_template, "fallback_content")

    @patch('shutil.copy2')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('os.walk')
    def test_copy_core_files_exclusions(self, mock_walk, mock_exists, mock_makedirs, mock_copy2, mock_input):
        # Setup mock for os.walk
        mock_exists.side_effect = lambda path: False if "valid.py" in path or "git_profiles" in path or "locks.json" in path or "cached.pyc" in path else True
        mock_walk.return_value = [
            ('/src/root/.agents/scripts', ['__pycache__', 'valid_dir'], ['git_profiles.json', 'locks.json', 'valid.py', 'cached.pyc'])
        ]
        
        bootstrap.copy_core_files()
        
        # Verify copy2 was called for valid.py but NOT for git_profiles.json, locks.json, or cached.pyc
        # Filter mock calls
        copied_files = []
        for call_args in mock_copy2.call_args_list:
            copied_files.append(os.path.basename(call_args[0][0]))
            
        self.assertIn("valid.py", copied_files)
        self.assertNotIn("git_profiles.json", copied_files)
        self.assertNotIn("locks.json", copied_files)
        self.assertNotIn("cached.pyc", copied_files)

    @patch('shutil.copy2')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('os.walk')
    def test_copy_core_files_force_update(self, mock_walk, mock_exists, mock_makedirs, mock_copy2, mock_input):
        mock_exists.return_value = True
        mock_walk.return_value = [
            ('/src/root/.agents/scripts', [], ['valid.py'])
        ]
        
        # Should not copy without force since it exists
        bootstrap.copy_core_files(force=False)
        mock_copy2.assert_not_called()
        
        # Should copy with force
        bootstrap.copy_core_files(force=True)
        mock_copy2.assert_called()

    def test_bootstrap_core_dirs_isolation(self, mock_input):
        import inspect
        source = inspect.getsource(bootstrap.copy_core_files)
        # Check that memory, tasks, issues, plans, tests are NOT in the copied core_dirs list
        self.assertNotIn("'.agents/memory'", source)
        self.assertNotIn("'.agents/tasks'", source)
        self.assertNotIn("'.agents/issues'", source)
        self.assertNotIn("'.agents/plans'", source)
        self.assertNotIn("'.agents/tests'", source)

if __name__ == '__main__':
    unittest.main()
