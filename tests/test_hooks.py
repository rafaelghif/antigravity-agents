import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "hooks"))

from scripts.hooks import pre_invoke_master, hook_utils

class TestHooks(unittest.TestCase):
    def test_detect_skills_from_text(self):
        self.assertIn("design", pre_invoke_master.detect_skills_from_text("fix button styling and tailwind css"))
        self.assertIn("architecture", pre_invoke_master.detect_skills_from_text("add postgres database schema and orm"))
        self.assertIn("security", pre_invoke_master.detect_skills_from_text("implement jwt auth and sanitize input"))
        self.assertIn("verification", pre_invoke_master.detect_skills_from_text("write pytest unit test for endpoint"))
        self.assertIn("devops", pre_invoke_master.detect_skills_from_text("create dockerfile and kubernetes manifest"))
        self.assertIn("code-quality", pre_invoke_master.detect_skills_from_text("arbitrary text"))

    def test_parse_skills_from_frontmatter_inline(self):
        fm = "skills: [architecture, verification, security]"
        skills = pre_invoke_master.parse_skills_from_frontmatter(fm)
        self.assertEqual(skills, ["architecture", "verification", "security"])

    def test_parse_skills_from_frontmatter_multiline(self):
        fm = "skills:\n  - architecture\n  - code-quality"
        skills = pre_invoke_master.parse_skills_from_frontmatter(fm)
        self.assertIn("architecture", skills)
        self.assertIn("code-quality", skills)

    def test_get_context_includes_grounding_baseline(self):
        ctx = pre_invoke_master.get_context(None)
        self.assertIn("=== CODEBASE GROUNDING BASELINE ===", ctx)
        self.assertIn("Ecosystem:", ctx)
        self.assertIn("OS/Arch:", ctx)

    def test_get_context_with_frameworks_and_test_runners(self):
        from unittest.mock import patch
        mock_grounding = {
            "ecosystems": {"node": ["package.json"]},
            "environment": {"platform": "linux", "architecture": "x86_64", "machine": "x86_64"},
            "package_managers": {"lockfile_managed": ["pnpm"], "available_cli": ["git", "pnpm"]},
            "frameworks": [{"name": "React", "ecosystem": "node", "package": "react"}, {"name": "Next.js", "ecosystem": "node", "package": "next"}],
            "testing": ["vitest", "playwright"],
            "dependencies": {"node": ["react", "next"]},
        }
        with patch("scripts.grounding.ground_workspace", return_value=mock_grounding):
            ctx = pre_invoke_master.get_context(None)
            self.assertIn("Frameworks: React, Next.js", ctx)
            self.assertIn("Test Runners: vitest, playwright", ctx)
            self.assertIn("OS/Arch: linux (x86_64)", ctx)
            self.assertIn("Tooling: Lockfile: pnpm | CLI: git, pnpm", ctx)

if __name__ == "__main__":
    unittest.main()
