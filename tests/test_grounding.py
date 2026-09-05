import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.grounding import detect_ecosystems, extract_dependencies, ground_workspace, inspect_project_layout

class TestGroundingEngine(unittest.TestCase):
    def test_detect_ecosystems(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir)
            (p / "package.json").write_text("{}")
            (p / "Cargo.toml").write_text("[package]")
            (p / "go.mod").write_text("module example.com/app")

            ecos = detect_ecosystems(p)
            self.assertIn("node", ecos)
            self.assertIn("rust", ecos)
            self.assertIn("go", ecos)
            self.assertNotIn("python", ecos)

    def test_extract_dependencies(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir)
            (p / "package.json").write_text(json.dumps({
                "dependencies": {"react": "^18.2.0"},
                "devDependencies": {"typescript": "^5.0.0"}
            }))
            (p / "requirements.txt").write_text("pydantic==2.5.0\npytest>=7.0.0\n")

            ecos = detect_ecosystems(p)
            deps = extract_dependencies(p, ecos)
            self.assertIn("react", deps.get("node", []))
            self.assertIn("typescript", deps.get("node", []))
            self.assertIn("pydantic", deps.get("python", []))

    def test_inspect_layout_ignores_internal_folders(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir)
            (p / "src").mkdir()
            (p / "tests").mkdir()
            (p / ".git").mkdir()
            (p / "node_modules").mkdir()

            layout = inspect_project_layout(p)
            dirs = layout.get("directories", [])
            self.assertIn("src", dirs)
            self.assertIn("tests", dirs)
            self.assertNotIn(".git", dirs)
            self.assertNotIn("node_modules", dirs)

    def test_detect_nested_monorepo_ecosystems(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir)
            (p / "apps" / "web").mkdir(parents=True)
            (p / "apps" / "web" / "package.json").write_text('{"dependencies": {"vue": "^3.0.0"}}')
            (p / "services" / "api").mkdir(parents=True)
            (p / "services" / "api" / "requirements.txt").write_text("fastapi>=0.100.0\n")

            ecos = detect_ecosystems(p)
            self.assertIn("node", ecos)
            self.assertIn("python", ecos)
            deps = extract_dependencies(p, ecos)
            self.assertIn("vue", deps.get("node", []))
            self.assertIn("fastapi", deps.get("python", []))

    def test_infer_ecosystem_from_source_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir)
            (p / "src").mkdir()
            (p / "src" / "main.py").write_text("print('hello')\n")

            ecos = detect_ecosystems(p)
            self.assertIn("python", ecos)
            deps = extract_dependencies(p, ecos)
            self.assertIn("python", deps)

    def test_ground_workspace_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir)
            data = ground_workspace(p)
            self.assertIn("root", data)
            self.assertIn("ecosystems", data)
            self.assertIn("dependencies", data)
            self.assertIn("layout", data)
            self.assertIn("git", data)
            self.assertIn("environment", data)
            self.assertIn("package_managers", data)
            self.assertIn("frameworks", data)
            self.assertIn("testing", data)
            self.assertIn("linters_formatters", data)
            self.assertIn("ci_cd", data)
            self.assertIn("project_type", data)
            self.assertIn("quality_gates", data)
            self.assertIn("os", data["environment"])
            self.assertIn("python", data["environment"])

    def test_detect_package_managers_and_frameworks(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir)
            (p / "pnpm-lock.yaml").write_text("# lockfile")
            (p / "package.json").write_text(json.dumps({
                "name": "my-app",
                "dependencies": {"next": "14.0.0", "react": "18.2.0"}
            }))
            ecos = detect_ecosystems(p)
            deps = extract_dependencies(p, ecos)
            from scripts.grounding import detect_package_managers, detect_frameworks, detect_project_classification
            pms = detect_package_managers(p)
            self.assertIn("pnpm", pms["lockfile_managed"])
            fws = detect_frameworks(p, deps)
            fw_names = [f["name"] for f in fws]
            self.assertIn("Next.js", fw_names)
            self.assertIn("React", fw_names)
            ptype = detect_project_classification(p, ecos, fws)
            self.assertEqual(ptype, "Web Application")

    def test_detect_backend_api_framework(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir)
            (p / "requirements.txt").write_text("fastapi>=0.100.0\nuvicorn>=0.23.0\n")
            ecos = detect_ecosystems(p)
            deps = extract_dependencies(p, ecos)
            from scripts.grounding import detect_frameworks, detect_project_classification
            fws = detect_frameworks(p, deps)
            fw_names = [f["name"] for f in fws]
            self.assertIn("FastAPI", fw_names)
            ptype = detect_project_classification(p, ecos, fws)
            self.assertEqual(ptype, "Backend API Service")

    def test_extract_pyproject_deps_no_hallucinations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir)
            (p / "pyproject.toml").write_text("""[project]
name = "my-awesome-service"
version = "0.1.0"
description = "A sample service"
readme = "README.md"
dependencies = [
    "httpx>=0.24.0",
    "pydantic[email]~=2.5.0; python_version >= '3.10'",
    "fastapi"
]
[project.optional-dependencies]
dev = ["pytest>=7.0.0", "black"]
""")
            ecos = detect_ecosystems(p)
            deps = extract_dependencies(p, ecos)
            py_deps = deps.get("python", [])
            self.assertIn("httpx", py_deps)
            self.assertIn("pydantic", py_deps)
            self.assertIn("fastapi", py_deps)
            self.assertIn("pytest", py_deps)
            # Critical anti-hallucination verification: metadata must NEVER be extracted as dependencies
            for forbidden in ("name", "version", "description", "readme", "README.md", "0.1.0", "my-awesome-service", "dependencies"):
                self.assertNotIn(forbidden, py_deps)

    def test_extract_cargo_deps_no_hallucinations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir)
            (p / "Cargo.toml").write_text("""[package]
name = "my_crate"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = { version = "1.0", features = ["full"] }
serde = "1.0"
""")
            ecos = detect_ecosystems(p)
            deps = extract_dependencies(p, ecos)
            rust_deps = deps.get("rust", [])
            self.assertIn("tokio", rust_deps)
            self.assertIn("serde", rust_deps)
            for forbidden in ("name", "version", "edition", "0.1.0", "my_crate", "package", "dependencies"):
                self.assertNotIn(forbidden, rust_deps)

    def test_detect_monorepo_nested_lockfiles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir)
            (p / "apps" / "web").mkdir(parents=True)
            (p / "apps" / "web" / "pnpm-lock.yaml").write_text("# lockfile")
            (p / "backend").mkdir()
            (p / "backend" / "poetry.lock").write_text("# lockfile")
            from scripts.grounding import detect_package_managers
            pms = detect_package_managers(p)
            self.assertIn("pnpm", pms["lockfile_managed"])
            self.assertIn("poetry", pms["lockfile_managed"])

    def test_detect_environment_has_architecture(self):
        from scripts.grounding import detect_environment
        with tempfile.TemporaryDirectory() as tmpdir:
            env = detect_environment(Path(tmpdir))
            self.assertIn("architecture", env)
            self.assertIn("machine", env)
            self.assertEqual(env["architecture"], env["machine"])

if __name__ == "__main__":
    unittest.main()


