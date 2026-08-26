import unittest
import os
import sys
import tempfile
from pathlib import Path

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.self_learner import (
    extract_learning_from_user_input,
    save_learned_rule,
    save_project_preference,
    normalize_rule
)

class TestSelfLearner(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.rules_path = Path(self.tmp_dir.name) / "rules.md"
        self.memory_path = Path(self.tmp_dir.name) / "memory.md"
        
        self.rules_path.write_text("# Procedural Memory Rules\n\n- **[NO_TRASH]**: Never leave temporary files.\n", encoding="utf-8")
        self.memory_path.write_text("# Memory\n\n## 📌 Learned Rules & User Preferences\n- Follow strict DRY.\n", encoding="utf-8")

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_extract_learning_from_corrections(self):
        # Negative / mandate signals
        text1 = "jangan pernah pakai inline style di react, harus pakai tailwind"
        learned1 = extract_learning_from_user_input(text1)
        self.assertIsNotNone(learned1)
        self.assertTrue("tailwind" in learned1.lower() or "inline" in learned1.lower())

        # Reminder / priority signals
        text2 = "ingat ya selalu dahulukan unit testing sebelum commit"
        learned2 = extract_learning_from_user_input(text2)
        self.assertIsNotNone(learned2)
        self.assertTrue("unit testing" in learned2.lower())

        # Casual greeting - should NOT trigger learning
        text3 = "halo bro, gimana kabarnya?"
        learned3 = extract_learning_from_user_input(text3)
        self.assertIsNone(learned3)

    def test_save_learned_rule_deduplication(self):
        rule = "Dahulukan unit testing sebelum commit"
        # First save should succeed
        saved1 = save_learned_rule(rule, self.rules_path, tag="TEST_MANDATE")
        self.assertTrue(saved1)
        
        content = self.rules_path.read_text(encoding="utf-8")
        self.assertIn("Dahulukan unit testing", content)

        # Second save of identical rule should be rejected (deduplicated)
        saved2 = save_learned_rule(rule, self.rules_path, tag="TEST_MANDATE")
        self.assertFalse(saved2)

    def test_save_project_preference(self):
        pref = "User prefers bun over pnpm"
        saved = save_project_preference(pref, self.memory_path)
        self.assertTrue(saved)

        content = self.memory_path.read_text(encoding="utf-8")
        self.assertIn("User prefers bun over pnpm", content)

    def test_normalize_rule(self):
        self.assertEqual(normalize_rule("  Jangan Gunakan Any!  "), "jangan gunakan any")

if __name__ == '__main__':
    unittest.main()
