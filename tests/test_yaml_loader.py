import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.yaml_loader import _fallback_yaml_load, load_yaml

class TestYamlLoader(unittest.TestCase):
    def test_fallback_basic_dict(self):
        sample = """
        name: test-app
        status: IN_PROGRESS
        enabled: true
        count: 42
        """
        parsed = _fallback_yaml_load(sample)
        self.assertEqual(parsed.get("name"), "test-app")
        self.assertEqual(parsed.get("status"), "IN_PROGRESS")
        self.assertEqual(parsed.get("enabled"), True)
        self.assertEqual(parsed.get("count"), 42)

    def test_fallback_nested_dict_and_lists(self):
        sample = """
        tasks:
          worker-1:
            command: python3 worker.py
            depends_on: []
          worker-2:
            command: python3 reporter.py
            depends_on: [worker-1]
        """
        parsed = _fallback_yaml_load(sample)
        self.assertIn("tasks", parsed)
        self.assertEqual(parsed["tasks"]["worker-1"]["command"], "python3 worker.py")
        self.assertEqual(parsed["tasks"]["worker-1"]["depends_on"], [])
        self.assertEqual(parsed["tasks"]["worker-2"]["depends_on"], ["worker-1"])

    def test_fallback_bullet_lists(self):
        sample = """
        objectives:
          - First objective
          - Second objective
        """
        parsed = _fallback_yaml_load(sample)
        self.assertEqual(parsed.get("objectives"), ["First objective", "Second objective"])

if __name__ == '__main__':
    unittest.main()
