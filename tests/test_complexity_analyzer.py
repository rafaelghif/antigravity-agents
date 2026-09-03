import ast
import unittest
from pathlib import Path

from scripts.complexity_analyzer import EnterpriseL9Visitor

class TestComplexityAnalyzer(unittest.TestCase):
    def test_clean_code_passes(self):
        code = "def process_data(records: list) -> int:\n    count = 0\n    for r in records:\n        count += len(r)\n    return count\n"
        visitor = EnterpriseL9Visitor("process.py")
        visitor.visit(ast.parse(code))
        self.assertEqual(visitor.max_depth, 1)
        self.assertEqual(len(visitor.empty_excepts), 0)
        self.assertEqual(len(visitor.nested_loops), 0)

    def test_nested_loop_flagged(self):
        code = "def matrix_mult(a: list, b: list) -> list:\n    for i in a:\n        for j in b:\n            print(i, j)\n"
        visitor = EnterpriseL9Visitor("matrix.py")
        visitor.visit(ast.parse(code))
        self.assertGreater(visitor.max_depth, 1)
        self.assertEqual(len(visitor.nested_loops), 1)

    def test_empty_except_flagged(self):
        code = "try:\n    val = 1 / 0\nexcept ZeroDivisionError:\n    pass\n"
        visitor = EnterpriseL9Visitor("danger.py")
        visitor.visit(ast.parse(code))
        self.assertGreaterEqual(len(visitor.empty_excepts), 1)

if __name__ == "__main__":
    unittest.main()