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

    def test_scan_workspace_dotnet_sub_frameworks(self):
        # Create a csproj that includes WPF and ASP.NET Core Web Sdk
        with open("project.csproj", 'w', encoding='utf-8') as f:
            f.write('<Project Sdk="Microsoft.NET.Sdk.Web">\n<PropertyGroup>\n<TargetFramework>net8.0</TargetFramework>\n<UseWPF>true</UseWPF>\n</PropertyGroup>\n</Project>')
        results = recon.scan_workspace()
        self.assertEqual(results["main_stack"], "dotnet")
        self.assertIn(".NET Core (C#)", results["stack"])
        self.assertIn("WPF", results["stack"])
        self.assertIn("ASP.NET Core", results["stack"])
        self.assertEqual(results["test_command"], "dotnet test")
        self.assertEqual(results["recommended_architecture"], "Clean Architecture / Domain-Driven Design (DDD)")

    def test_scan_workspace_php_laravel_pest(self):
        # Artisan file + composer.json referencing pest
        with open("composer.json", 'w', encoding='utf-8') as f:
            f.write('{"require-dev": {"pestphp/pest": "^2.0"}}')
        with open("artisan", 'w', encoding='utf-8') as f:
            f.write('')
        results = recon.scan_workspace()
        self.assertEqual(results["main_stack"], "php")
        self.assertIn("PHP (Laravel)", results["stack"])
        self.assertEqual(results["test_command"], "php artisan test")
        self.assertEqual(results["recommended_architecture"], "MVC (Model-View-Controller) / Clean Architecture")

    def test_scan_workspace_php_phpunit(self):
        # PHPUnit file
        with open("composer.json", 'w', encoding='utf-8') as f:
            f.write('{"require-dev": {"phpunit/phpunit": "^10.0"}}')
        results = recon.scan_workspace()
        self.assertEqual(results["main_stack"], "php")
        self.assertIn("PHP", results["stack"])
        self.assertEqual(results["test_command"], "./vendor/bin/phpunit")
        self.assertEqual(results["recommended_architecture"], "MVC (Model-View-Controller)")

    def test_scan_workspace_ruby_rspec(self):
        # Gemfile + spec dir
        with open("Gemfile", 'w', encoding='utf-8') as f:
            f.write("gem 'rails'\ngem 'rspec-rails'")
        os.makedirs("spec", exist_ok=True)
        results = recon.scan_workspace()
        self.assertEqual(results["main_stack"], "ruby")
        self.assertIn("Ruby (Ruby on Rails)", results["stack"])
        self.assertEqual(results["test_command"], "bundle exec rspec")
        self.assertEqual(results["recommended_architecture"], "MVC (Model-View-Controller)")

    def test_scan_workspace_go_gin(self):
        with open("go.mod", 'w', encoding='utf-8') as f:
            f.write("module test\nrequire github.com/gin-gonic/gin v1.9.0")
        results = recon.scan_workspace()
        self.assertEqual(results["main_stack"], "go")
        self.assertIn("Go (Golang) (Gin)", results["stack"])
        self.assertEqual(results["test_command"], "go test ./...")
        self.assertEqual(results["recommended_architecture"], "Layered (Controller-Service-Repository) / Hexagonal")

    def test_scan_workspace_rust_axum(self):
        with open("Cargo.toml", 'w', encoding='utf-8') as f:
            f.write("[dependencies]\naxum = \"0.6\"")
        results = recon.scan_workspace()
        self.assertEqual(results["main_stack"], "rust")
        self.assertIn("Rust (Axum)", results["stack"])
        self.assertEqual(results["test_command"], "cargo test")
        self.assertEqual(results["recommended_architecture"], "Layered Architecture (Hexagonal / Clean)")

    def test_scan_workspace_java_gradle(self):
        with open("build.gradle", 'w', encoding='utf-8') as f:
            f.write("dependencies {\nimplementation 'org.springframework.boot:spring-boot-starter'\n}")
        results = recon.scan_workspace()
        self.assertEqual(results["main_stack"], "java")
        self.assertIn("Java (Spring Boot)", results["stack"])
        self.assertEqual(results["test_command"], "gradle test")
        self.assertEqual(results["recommended_architecture"], "Clean Architecture / Domain-Driven Design (DDD) / Hexagonal")

    def test_scan_workspace_dart_flutter(self):
        with open("pubspec.yaml", 'w', encoding='utf-8') as f:
            f.write("dependencies:\n  flutter:\n    sdk: flutter")
        results = recon.scan_workspace()
        self.assertEqual(results["main_stack"], "dart")
        self.assertIn("Dart (Flutter)", results["stack"])
        self.assertEqual(results["test_command"], "flutter test")
        self.assertEqual(results["recommended_architecture"], "BLoC / Feature-First Layered Architecture")

    def test_scan_workspace_elixir_phoenix(self):
        with open("mix.exs", 'w', encoding='utf-8') as f:
            f.write("defp deps do\n[{:phoenix, \"~> 1.7\"}]\nend")
        results = recon.scan_workspace()
        self.assertEqual(results["main_stack"], "elixir")
        self.assertIn("Elixir (Phoenix)", results["stack"])
        self.assertEqual(results["test_command"], "mix test")
        self.assertEqual(results["recommended_architecture"], "MVC (Model-View-Controller) / Context-driven")

    def test_scan_workspace_swift_vapor(self):
        with open("Package.swift", 'w', encoding='utf-8') as f:
            f.write(".package(url: \"https://github.com/vapor/vapor.git\", from: \"4.0.0\")")
        results = recon.scan_workspace()
        self.assertEqual(results["main_stack"], "swift")
        self.assertIn("Swift (Vapor)", results["stack"])
        self.assertEqual(results["test_command"], "swift test")
        self.assertEqual(results["recommended_architecture"], "MVC (Model-View-Controller)")

    def test_scan_workspace_cpp_cmake(self):
        with open("CMakeLists.txt", 'w', encoding='utf-8') as f:
            f.write("cmake_minimum_required(VERSION 3.10)")
        results = recon.scan_workspace()
        self.assertEqual(results["main_stack"], "cpp")
        self.assertIn("C++", results["stack"])
        self.assertEqual(results["test_command"], "ctest")
        self.assertEqual(results["recommended_architecture"], "Modular Library / Layered Architecture")

    def test_scan_workspace_react_frontend(self):
        # Package.json referencing react
        with open("package.json", 'w', encoding='utf-8') as f:
            f.write('{"dependencies": {"react": "^18.2.0"}}')
        results = recon.scan_workspace()
        self.assertEqual(results["main_stack"], "node")
        self.assertIn("React", results["stack"])
        self.assertEqual(results["recommended_architecture"], "Atomic Design / Component-driven")

if __name__ == '__main__':
    unittest.main()
