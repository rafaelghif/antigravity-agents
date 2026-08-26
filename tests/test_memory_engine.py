import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from scripts.hooks import pre_invoke_master, post_invoke_telemetry

class TestMemoryEngine(unittest.TestCase):
    def test_get_context_loads_memory(self):
        # Ensure get_context includes memory, anchor, and rules when available
        context = pre_invoke_master.get_context(None)
        self.assertIsInstance(context, str)

    def test_skill_detection_logic(self):
        # Test keyword matching for skill auto-injection
        skills = pre_invoke_master.detect_skills_from_text("tolong buatkan UI page login dengan Tailwind CSS")
        self.assertIn("design", skills)
        self.assertIn("code-quality", skills)

        skills_sec = pre_invoke_master.detect_skills_from_text("implement JWT authentication and password hashing")
        self.assertIn("security", skills_sec)

        skills_arch = pre_invoke_master.detect_skills_from_text("design database schema migration for orders")
        self.assertIn("architecture", skills_arch)

        skills_cave = pre_invoke_master.detect_skills_from_text("tolong hemat token dengan gaya caveman")
        self.assertIn("caveman", skills_cave)

    def test_update_project_memory_runs_safely(self):
        # Ensure memory consolidation runs without errors
        post_invoke_telemetry.update_project_memory()
        memory_path = Path('.agents/brain/memory.md')
        self.assertTrue(memory_path.exists())

if __name__ == '__main__':
    unittest.main()
