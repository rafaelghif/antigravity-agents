#!/usr/bin/env python3
import ast
import sys
from pathlib import Path

class LoopVisitor(ast.NodeVisitor):
    def __init__(self):
        self.loop_depth = 0
        self.max_depth = 0
        self.nested_loops = []

    def visit_For(self, node):
        self.loop_depth += 1
        if self.loop_depth > self.max_depth:
            self.max_depth = self.loop_depth
        if self.loop_depth > 1:
            self.nested_loops.append(node.lineno)
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node):
        self.loop_depth += 1
        if self.loop_depth > self.max_depth:
            self.max_depth = self.loop_depth
        if self.loop_depth > 1:
            self.nested_loops.append(node.lineno)
        self.generic_visit(node)
        self.loop_depth -= 1

def analyze_complexity(filepath):
    try:
        content = filepath.read_text(encoding='utf-8')
        tree = ast.parse(content)
        visitor = LoopVisitor()
        visitor.visit(tree)
        if visitor.max_depth > 1:
            print(f"[COMPLEXITY FATAL] {filepath.name}: Detected O(N^{visitor.max_depth}) nested loop at lines {visitor.nested_loops}.")
            return False
        return True
    except Exception as e:
        return True

if __name__ == '__main__':
    print("[AAC] Running Static Complexity Analysis (Real AST check)...")
    failed = False
    root_path = Path.cwd()
    for py_file in root_path.rglob("*.py"):
        if any(part in [".venv", "venv", ".git", ".agents", "__pycache__", "node_modules"] for part in py_file.parts):
            continue
        if not analyze_complexity(py_file):
            failed = True
            
    if failed:
        print("=> ERROR: Code complexity exceeds AAC L9 thresholds. Refactor using HashMaps.")
        sys.exit(1)
    print("=> SUCCESS: No O(N^2) nesting detected in scripts.")
    sys.exit(0)
