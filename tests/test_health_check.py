import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.health_check import HealthChecker


class TestHealthCheck(unittest.TestCase):
    def setUp(self):
        self.checker = HealthChecker(root=ROOT)

    def test_health_check_real_workspace(self):
        report = self.checker.run_all()
        self.assertEqual(report["status"], "HEALTHY")
        self.assertEqual(report["passed_checks"], 14)
        self.assertEqual(report["total_checks"], 14)
        self.assertEqual(len(report["issues"]), 0)

    def test_missing_agents_detection(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            checker = HealthChecker(root=Path(tmpdir))
            passed = checker.check_agents()
            self.assertFalse(passed)
            self.assertIn("missing_agents", checker.results)
            self.assertFalse(checker.results["missing_agents"]["passed"])

    def test_missing_skills_detection(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            checker = HealthChecker(root=Path(tmpdir))
            passed = checker.check_skills()
            self.assertFalse(passed)
            self.assertIn("missing_skills", checker.results)

    def test_missing_rules_detection(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            checker = HealthChecker(root=Path(tmpdir))
            passed = checker.check_rules()
            self.assertFalse(passed)
            self.assertIn("missing_rules", checker.results)

    def test_broken_scripts_detection(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            scripts_dir = Path(tmpdir) / "scripts"
            scripts_dir.mkdir(parents=True)
            bad_script = scripts_dir / "broken.py"
            bad_script.write_text("def broken_syntax(:\n", encoding="utf-8")

            checker = HealthChecker(root=Path(tmpdir))
            passed = checker.check_broken_scripts()
            self.assertFalse(passed)
            self.assertEqual(len(checker.results["broken_scripts"]["errors"]), 1)

    def test_deterministic_self_repair(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            checker = HealthChecker(root=target, repair=True)
            repaired = checker.execute_repairs()
            self.assertTrue(len(repaired) >= 3)
            self.assertTrue((target / ".agents" / "scratch").is_dir())
            self.assertTrue((target / "handoff.json").is_file())
            self.assertTrue((target / ".agents" / "brain" / "env-required.json").is_file())
            self.assertTrue((target / ".gitignore").is_file())


if __name__ == "__main__":
    unittest.main()
