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
        
        from unittest.mock import MagicMock
        self.run_patcher = patch('subprocess.run')
        self.mock_run = self.run_patcher.start()
        
        def run_side_effect(cmd, *args, **kwargs):
            if len(cmd) >= 3 and cmd[0] == 'git' and cmd[1] == 'clone':
                src = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
                dest = cmd[-1]
                import shutil
                shutil.copytree(os.path.join(src, ".agents"), os.path.join(dest, ".agents"), dirs_exist_ok=True)
                for f in ["AGENTS.md", "helper.sh", "helper.ps1", "bootstrap.sh", "bootstrap.ps1", "Dockerfile"]:
                    src_f = os.path.join(src, f)
                    if os.path.exists(src_f):
                        shutil.copy2(src_f, os.path.join(dest, f))
                return MagicMock(returncode=0)
            return MagicMock(returncode=0)
        self.mock_run.side_effect = run_side_effect
        
    def tearDown(self):
        self.run_patcher.stop()
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

        # Verify new synchronized files
        self.assertTrue(os.path.exists("Dockerfile"))
        self.assertTrue(os.path.exists("bootstrap.sh"))
        self.assertTrue(os.path.exists("bootstrap.ps1"))
        self.assertTrue(os.path.exists(".agents/projects.example"))
        self.assertTrue(os.path.exists(".agents/docs/context_map.md"))
        self.assertTrue(os.path.exists(".agents/dashboard/index.html"))
        self.assertTrue(os.path.exists(".agents/mcp_config.json"))

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

    def test_bootstrap_clone_failure_fallback(self, mock_input):
        from unittest.mock import MagicMock
        self.mock_run.side_effect = None
        self.mock_run.return_value = MagicMock(returncode=1, stderr="Mock Git Clone Failed")
        
        bootstrap.run(["FallbackClone", "python", "clean"])
        self.assertTrue(os.path.exists("AGENTS.md"))

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
        mock_exists.side_effect = lambda path: False if "valid.py" in path or "git_profiles" in path or "locks.json" in path or "cached.pyc" in path or "memory" in path or "projects.example" in path else True
        mock_walk.return_value = [
            ('/src/root/.agents/scripts', ['__pycache__', 'valid_dir'], ['git_profiles.json', 'locks.json', 'valid.py', 'cached.pyc'])
        ]
        
        bootstrap.copy_core_files('/src/root')
        
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
        mock_exists.side_effect = lambda path: False if "memory" in path or "projects.example" in path else True
        mock_walk.return_value = [
            ('/src/root/.agents/scripts', [], ['valid.py'])
        ]
        
        # Should not copy without force since it exists
        bootstrap.copy_core_files('/src/root', force=False)
        mock_copy2.assert_not_called()
        
        # Should copy with force
        bootstrap.copy_core_files('/src/root', force=True)
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

    @patch('shutil.copy2')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('os.walk')
    def test_copy_core_files_transient_exclusions(self, mock_walk, mock_exists, mock_makedirs, mock_copy2, mock_input):
        mock_exists.side_effect = lambda path: False if "memory" in path else True
        mock_walk.return_value = [
            ('/src/root/.agents/scripts', [], [
                'token_budget.json', 'active_context.md', 'sync_cache.json', 
                'cooldowns.json', 'upgrade_state.json', 'projects.json'
            ])
        ]
        
        bootstrap.copy_core_files('/src/root', force=True)
        
        copied_files = [os.path.basename(call_args[0][0]) for call_args in mock_copy2.call_args_list]
        transient_files = {
            'token_budget.json', 'active_context.md', 'sync_cache.json', 
            'cooldowns.json', 'upgrade_state.json', 'projects.json'
        }
        for f in transient_files:
            self.assertNotIn(f, copied_files)

if __name__ == '__main__':
    unittest.main()

