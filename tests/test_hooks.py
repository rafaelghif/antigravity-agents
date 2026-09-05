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

if __name__ == "__main__":
    unittest.main()
