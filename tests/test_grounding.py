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

if __name__ == "__main__":
    unittest.main()

