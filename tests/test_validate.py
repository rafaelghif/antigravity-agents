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

if __name__ == '__main__':
    unittest.main()
