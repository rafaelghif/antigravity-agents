import unittest
import os
import sys
from pathlib import Path

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.upgrade import parse_semver, is_newer_version

class TestUpgrade(unittest.TestCase):
    def test_parse_semver(self):
        self.assertEqual(parse_semver("v4.18.0"), (4, 18, 0))
        self.assertEqual(parse_semver("4.18.0"), (4, 18, 0))
        self.assertEqual(parse_semver("v5.0.0-rc1"), (5, 0, 0))
        self.assertEqual(parse_semver("latest"), (0, 0, 0))

    def test_is_newer_version(self):
        self.assertTrue(is_newer_version("v4.19.0", "4.18.0"))
        self.assertTrue(is_newer_version("v5.0.0", "v4.18.0"))
        self.assertFalse(is_newer_version("v4.18.0", "4.18.0"))
        self.assertFalse(is_newer_version("v4.17.0", "4.18.0"))

if __name__ == '__main__':
    unittest.main()
