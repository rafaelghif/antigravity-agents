import sys
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from scripts import verify

class TestVerify(unittest.TestCase):
    def test_detect(self):
        checks = verify.detect()
        self.assertIsInstance(checks, list)

    @patch('sys.argv', ['verify.py'])
    @patch('subprocess.run')
    def test_main(self, mock_run):
        # The verify main script should execute without throwing errors
        mock_run.return_value.returncode = 0
        self.assertEqual(verify.main(), 0)

if __name__ == '__main__':
    unittest.main()
