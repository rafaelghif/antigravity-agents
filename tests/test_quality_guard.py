import unittest
import os
import tempfile
import sys
from pathlib import Path

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.test_quality_guard import analyze_test_file

class TestQualityGuard(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_detects_sham_callable_test(self):
        # A test that only asserts callable() without testing input/output
        content = """
import unittest

def add(a, b):
    return a + b

class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertTrue(callable(add))
"""
        filepath = Path(self.temp_dir.name) / "test_math.py"
        filepath.write_text(content)
        is_valid, errors = analyze_test_file(filepath)
        self.assertFalse(is_valid)
        self.assertTrue(any("sham" in e.lower() or "callable" in e.lower() for e in errors))

    def test_detects_empty_test(self):
        content = """
import unittest

class TestEmpty(unittest.TestCase):
    def test_nothing(self):
        pass
"""
        filepath = Path(self.temp_dir.name) / "test_empty.py"
        filepath.write_text(content)
        is_valid, errors = analyze_test_file(filepath)
        self.assertFalse(is_valid)
        self.assertTrue(any("empty" in e.lower() or "no assertions" in e.lower() for e in errors))

    def test_passes_real_behavioral_test(self):
        content = """
import unittest

def add(a, b):
    return a + b

class TestMath(unittest.TestCase):
    def test_add(self):
        result = add(2, 3)
        self.assertEqual(result, 5)
"""
        filepath = Path(self.temp_dir.name) / "test_real.py"
        filepath.write_text(content)
        is_valid, errors = analyze_test_file(filepath)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

if __name__ == '__main__':
    unittest.main()
