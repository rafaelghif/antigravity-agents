import unittest
import os
import tempfile
import sys
from pathlib import Path

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.dry_guard import detect_duplicates, analyze_workspace

class TestDryGuard(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_detects_copy_pasted_code_across_files(self):
        duplicate_block = """
def calculate_tax(amount, rate):
    discount = 0.05
    base = amount * (1 - discount)
    tax = base * rate
    surcharge = tax * 0.02
    total = base + tax + surcharge
    return round(total, 2)
"""
        file1 = Path(self.temp_dir.name) / "billing.py"
        file2 = Path(self.temp_dir.name) / "checkout.py"

        file1.write_text(f"# Billing module\n{duplicate_block}\ndef other(): pass\n")
        file2.write_text(f"# Checkout module\n{duplicate_block}\ndef finalize(): pass\n")

        duplicates = detect_duplicates([file1, file2], min_lines=5)
        self.assertTrue(len(duplicates) > 0)
        
        dup = duplicates[0]
        files_involved = [loc[0].name for loc in dup['locations']]
        self.assertIn("billing.py", files_involved)
        self.assertIn("checkout.py", files_involved)

    def test_ignores_unique_code(self):
        file1 = Path(self.temp_dir.name) / "mod1.py"
        file2 = Path(self.temp_dir.name) / "mod2.py"

        file1.write_text("""
def alpha(x):
    y = x * 2
    z = y + 10
    return z
""")
        file2.write_text("""
def beta(name):
    greeting = f"Hello {name}"
    print(greeting)
    return greeting.strip()
""")

        duplicates = detect_duplicates([file1, file2], min_lines=5)
        self.assertEqual(len(duplicates), 0)

if __name__ == '__main__':
    unittest.main()
