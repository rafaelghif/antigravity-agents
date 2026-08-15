import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from scripts import verify

class TestVerify(unittest.TestCase):
    def test_detect(self):
        checks = verify.detect()
        self.assertIsInstance(checks, list)

    def test_main(self):
        # The verify main script should execute without throwing errors
        self.assertEqual(verify.main(), 0)

if __name__ == '__main__':
    unittest.main()
