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

    def test_scan_workspace_dotnet_core(self):
        # Create dummy .csproj for .NET Core
        with open("project.csproj", 'w', encoding='utf-8') as f:
            f.write('<Project Sdk="Microsoft.NET.Sdk">\n<PropertyGroup>\n<TargetFramework>net8.0</TargetFramework>\n</PropertyGroup>\n</Project>')
            
        results = recon.scan_workspace()
        self.assertEqual(results["main_stack"], "dotnet")
        self.assertIn(".NET Core (C#)", results["stack"])
        self.assertEqual(results["test_command"], "dotnet test")
        self.assertEqual(results["build_command"], "dotnet build")

    def test_scan_workspace_dotnet_framework(self):
        # Create dummy .csproj for .NET Framework
        with open("project.csproj", 'w', encoding='utf-8') as f:
            f.write('<Project>\n<PropertyGroup>\n<TargetFrameworkVersion>v4.8</PropertyGroup>\n</Project>')
            
        results = recon.scan_workspace()
        self.assertEqual(results["main_stack"], "dotnet")
        self.assertIn(".NET Framework (C#)", results["stack"])
        self.assertEqual(results["test_command"], "vstest.console.exe")
        self.assertEqual(results["build_command"], "nuget restore && msbuild")

    def test_setup_projects_json(self):
        scan_results = {
            "stack": ".NET Core (C#)",
            "main_stack": "dotnet",
            "test_command": "dotnet test"
        }
        recon.setup_projects_json(scan_results)
        projects_file = ".agents/projects.json"
        self.assertTrue(os.path.exists(projects_file))
        
        import json
        with open(projects_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        projects = data.get("projects", [])
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["name"], "main-project")
        self.assertEqual(projects[0]["path"], ".")
        self.assertEqual(projects[0]["stack"], "dotnet")
        self.assertEqual(projects[0]["test_command"], "dotnet test")

if __name__ == '__main__':
    unittest.main()
