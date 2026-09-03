import json
import tempfile
import unittest
from pathlib import Path

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
