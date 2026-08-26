import unittest
import os
import tempfile
import sys
from pathlib import Path

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.git_hygiene_guard import is_scratch_file, clean_scratch_files, find_scratch_files

class TestGitHygieneGuard(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_identifies_scratch_filenames(self):
        self.assertTrue(is_scratch_file(Path("scratch.py")))
        self.assertTrue(is_scratch_file(Path("test_scratch.py")))
        self.assertTrue(is_scratch_file(Path("tmp_test.py")))
        self.assertTrue(is_scratch_file(Path("temp_debug.js")))
        self.assertTrue(is_scratch_file(Path("poc_reproduce.ts")))
        self.assertTrue(is_scratch_file(Path(".agents/scratch/dummy.txt")))
        self.assertTrue(is_scratch_file(Path("dump.tmp")))
        self.assertTrue(is_scratch_file(Path("backup.bak")))

        # Legitimate project files should NOT be identified as scratch
        self.assertFalse(is_scratch_file(Path("src/index.ts")))
        self.assertFalse(is_scratch_file(Path("tests/test_dry_guard.py")))
        self.assertFalse(is_scratch_file(Path(".agents/scratch/.gitkeep")))
        self.assertFalse(is_scratch_file(Path("scripts/validate.py")))

    def test_cleans_scratch_files_automatically(self):
        scratch1 = self.root / "tmp_debug.py"
        scratch2 = self.root / "scratch_poc.py"
        keep_file = self.root / "legit_service.py"

        scratch1.write_text("print('debugging')")
        scratch2.write_text("print('poc')")
        keep_file.write_text("def work(): pass")

        removed = clean_scratch_files(self.root)
        self.assertEqual(len(removed), 2)
        self.assertFalse(scratch1.exists())
        self.assertFalse(scratch2.exists())
        self.assertTrue(keep_file.exists())

if __name__ == '__main__':
    unittest.main()
