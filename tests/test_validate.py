import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from scripts import validate

class TestValidate(unittest.TestCase):
    def test_main(self):
        # Validate should pass cleanly on the current valid repository state
        self.assertEqual(validate.main(), 0)

    def test_is_framework_repo(self):
        # In this repo, install.sh exists with antigravity-agents.git
        self.assertTrue(validate.is_framework_repo())

    def test_consumer_mode_manifest(self):
        # Consumer required paths should be a subset of framework paths
        for path in validate.CONSUMER_REQUIRED_PATHS:
            self.assertIn(path, validate.REQUIRED_PATHS)

if __name__ == '__main__':
    unittest.main()

