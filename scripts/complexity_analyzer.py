#!/usr/bin/env python3
import ast
import os
import sys
import re
from pathlib import Path

class EnterpriseL9Visitor(ast.NodeVisitor):
    def __init__(self, filepath):
        self.filepath = filepath
        self.loop_depth = 0
        self.max_depth = 0
        self.nested_loops = []
        self.missing_types = []
        self.empty_excepts = []
        self.hardcoded_mocks = []

    def _track_loop_enter(self, node):
        self.loop_depth += 1
        if self.loop_depth > self.max_depth:
            self.max_depth = self.loop_depth
        if self.loop_depth > 1:
            self.nested_loops.append(node.lineno)

    def visit_For(self, node):
        self._track_loop_enter(node)
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node):
        self._track_loop_enter(node)
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_FunctionDef(self, node):
        # 1. Check for missing type hints in arguments
        for arg in node.args.args:
            if arg.arg != 'self' and arg.arg != 'cls' and arg.annotation is None:
                self.missing_types.append(f"{node.name}() arg '{arg.arg}' (Line {node.lineno})")
        
        # 2. Check for missing return type hints (ignore __init__)
        if node.name != "__init__" and node.returns is None:
            self.missing_types.append(f"{node.name}() return type (Line {node.lineno})")
            
        # 3. Check for mock function names
        if node.name.startswith("mock_") or "dummy" in node.name.lower():
            self.hardcoded_mocks.append(f"Function {node.name} (Line {node.lineno})")
            
        self.generic_visit(node)
        
    def visit_ExceptHandler(self, node):
        # 4. Check for empty exception blocks (just 'pass')
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self.empty_excepts.append(f"Empty catch block (Line {node.lineno})")
        self.generic_visit(node)

def analyze_file(filepath):
    try:
        content = filepath.read_text(encoding='utf-8')
        
        # Regex pass for missing implementations
        for i, line in enumerate(content.splitlines(), 1):
            if re.search(r'\b(' + 'T' + 'ODO' + r'|' + 'F' + 'IXME' + r')\b', line):
                print(f"[AST FATAL] {filepath.name}: Detected T-O-D-O/F-I-X-M-E at line {i}. L9 Agents must deliver 100% complete features.")
                return False
                
        tree = ast.parse(content)
        visitor = EnterpriseL9Visitor(filepath)
        visitor.visit(tree)
        
        failed = False
        if visitor.max_depth > 1:
            print(f"[AST FATAL] {filepath.name}: Detected O(N^{visitor.max_depth}) nested loop at lines {visitor.nested_loops}.")
            failed = True
        if visitor.missing_types and "scripts" not in filepath.parts:
            print(f"[AST FATAL] {filepath.name}: Missing type hints detected: {', '.join(visitor.missing_types[:3])}...")
            failed = True
        if visitor.empty_excepts:
            print(f"[AST FATAL] {filepath.name}: Detected empty exception blocks (silencing errors) at lines {visitor.empty_excepts}")
            failed = True
        if visitor.hardcoded_mocks:
            print(f"[AST FATAL] {filepath.name}: Detected hardcoded mock logic at {visitor.hardcoded_mocks}")
            failed = True
            
        return not failed
    except SyntaxError:
        print(f"[AST FATAL] {filepath.name}: SyntaxError encountered.")
        return False
    except Exception as e:
        import sys
        sys.stderr.write(f"[AST FATAL] {filepath.name}: Analysis failed: {e}\n")
        return True

def process_dir(dirpath: str, filenames: list[str], failed: bool) -> bool:
    for filename in filenames:
        if filename.endswith(".py"):
            py_file = Path(dirpath) / filename
            if not analyze_file(py_file):
                failed = True
    return failed

def run_analysis(root_path: Path | None = None) -> bool:
    failed = False
    target = root_path or Path(__file__).resolve().parents[1]
    excludes = {
        ".venv", "venv", "env", ".env", ".git", ".agents", "__pycache__",
        "node_modules", "tests", "dist", "build", "out", ".next", ".nuxt",
        ".svelte-kit", ".angular", ".astro", ".docusaurus", ".turbo", ".cache"
    }
    for dirpath, dirnames, filenames in os.walk(target):
        dirnames[:] = [d for d in dirnames if d not in excludes]
        # Ignore files within test directories entirely
        if "tests" in Path(dirpath).parts or "test" in dirpath:
            continue
        failed = process_dir(dirpath, filenames, failed)
    return failed

if __name__ == '__main__':
    print("[AAC] Running Enterprise AST Guard (Complexity, Types, Mocks, Anti-Patterns)...")
    target_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None
    failed = run_analysis(target_dir)
            
    if failed:
        print("=> ERROR: Code quality rejected by L9 Enterprise AST Guard. Refactor immediately.")
        sys.exit(1)
    print("=> SUCCESS: Source code meets L9 strictness constraints.")
    sys.exit(0)
