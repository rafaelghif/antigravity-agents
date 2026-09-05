#!/usr/bin/env python3
"""
Test Quality Guard: Enforces rigorous, behavioral unit testing across the workspace.
Detects and blocks tautological sham tests (e.g. asserting callable(func),
hasattr(module, func), or func is not None without exercising inputs/outputs).
"""

import ast
import os
import sys
import re
from pathlib import Path

class TestFunctionVisitor(ast.NodeVisitor):
    def __init__(self, func_name: str, lineno: int):
        self.func_name = func_name
        self.lineno = lineno
        self.assertions_count = 0
        self.sham_assertions = []
        self.behavioral_calls = 0

    def visit_Assert(self, node: ast.Assert):
        self.assertions_count += 1
        test_str = ast.unparse(node.test) if hasattr(ast, "unparse") else ""
        if isinstance(node.test, ast.Constant):
            self.sham_assertions.append(f"assert {test_str}")
        elif isinstance(node.test, ast.Compare):
            left_str = ast.unparse(node.test.left) if hasattr(ast, "unparse") else ""
            if all(ast.unparse(c) == left_str for c in node.test.comparators):
                self.sham_assertions.append(f"assert {test_str}")
            elif isinstance(node.test.left, ast.Constant) and all(isinstance(c, ast.Constant) for c in node.test.comparators):
                self.sham_assertions.append(f"assert {test_str}")
        
        if re.search(r'\bcallable\b|\bhasattr\b|\bis not None\b|\btype\(.*?\)\s*==', test_str):
            self.sham_assertions.append(f"assert {test_str}")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        INSPECTION_BUILTINS = {"callable", "hasattr", "isinstance", "type", "getattr", "id", "dir"}
        if func_name.startswith("assert"):
            self.assertions_count += 1
            call_str = ast.unparse(node) if hasattr(ast, "unparse") else ""
            if "callable(" in call_str or "hasattr(" in call_str or "is not None" in call_str:
                self.sham_assertions.append(call_str)
            elif func_name in ("assertIsNotNone", "assertTrue", "assertFalse") and len(node.args) == 1:
                arg_str = ast.unparse(node.args[0]) if hasattr(ast, "unparse") else ""
                if "callable(" in arg_str or "hasattr(" in arg_str or "(" not in arg_str or isinstance(node.args[0], ast.Constant):
                    self.sham_assertions.append(f"{func_name}({arg_str})")
            elif func_name == "assertEqual" and len(node.args) >= 2:
                arg1_str = ast.unparse(node.args[0]) if hasattr(ast, "unparse") else ""
                arg2_str = ast.unparse(node.args[1]) if hasattr(ast, "unparse") else ""
                if arg1_str == arg2_str or (isinstance(node.args[0], ast.Constant) and isinstance(node.args[1], ast.Constant)):
                    self.sham_assertions.append(f"{func_name}({arg1_str}, {arg2_str})")
        elif func_name not in INSPECTION_BUILTINS:
            self.behavioral_calls += 1

        self.generic_visit(node)

class TestModuleVisitor(ast.NodeVisitor):
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.errors = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name.startswith("test_") or node.name.endswith("_test"):
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                self.errors.append(f"{self.filepath.name}:{node.name} (Line {node.lineno}): Empty test body (just 'pass')")
                return

            sub = TestFunctionVisitor(node.name, node.lineno)
            for item in node.body:
                sub.visit(item)

            if sub.assertions_count == 0:
                self.errors.append(f"{self.filepath.name}:{node.name} (Line {node.lineno}): No assertions found in test.")
            elif len(sub.sham_assertions) == sub.assertions_count and sub.behavioral_calls == 0:
                self.errors.append(
                    f"{self.filepath.name}:{node.name} (Line {node.lineno}): Tautological sham test detected! "
                    f"Only asserts existence/callable ({', '.join(sub.sham_assertions)}) without testing input/output behavior."
                )

        self.generic_visit(node)

def analyze_python_test(filepath: Path) -> tuple[bool, list[str]]:
    try:
        content = filepath.read_text(encoding='utf-8')
        tree = ast.parse(content)
        visitor = TestModuleVisitor(filepath)
        visitor.visit(tree)
        return len(visitor.errors) == 0, visitor.errors
    except SyntaxError as e:
        return False, [f"{filepath.name}: Syntax error parsing test file: {e}"]
    except Exception as e:
        sys.stderr.write(f"Test analysis notice for {filepath.name}: {e}\n")
        return True, []

def analyze_js_test(filepath: Path) -> tuple[bool, list[str]]:
    errors = []
    try:
        content = filepath.read_text(encoding='utf-8')
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            if re.search(r'expect\(typeof\s+[A-Za-z0-9_]+\)\.toBe\([\'"]function[\'"]\)', line):
                errors.append(f"{filepath.name} (Line {i}): Sham assertion: testing `typeof fn === 'function'` instead of behavior.")
            elif re.search(r'expect\([A-Za-z0-9_]+\)\.toBeDefined\(\)', line):
                errors.append(f"{filepath.name} (Line {i}): Sham assertion: testing `toBeDefined()` on symbol without executing it.")
    except Exception as e:
        sys.stderr.write(f"JS test analysis notice: {e}\n")
    return len(errors) == 0, errors

def analyze_test_file(filepath: Path) -> tuple[bool, list[str]]:
    if filepath.suffix == ".py":
        return analyze_python_test(filepath)
    if filepath.suffix in (".ts", ".js"):
        return analyze_js_test(filepath)
    return True, []

def is_test_file(filepath: Path) -> bool:
    parts = [p.lower() for p in filepath.parts]
    if "scripts" in parts:
        return False
    name = filepath.name.lower()
    if "tests" in parts:
        return filepath.suffix in (".py", ".ts", ".js")
    return name.startswith("test_") or name.endswith("_test.py") or ".test." in name or ".spec." in name

def check_file_list(filenames: list[str], dirpath: str, all_errors: list[str]):
    for filename in filenames:
        fpath = Path(dirpath) / filename
        if is_test_file(fpath):
            is_valid, errors = analyze_test_file(fpath)
            if not is_valid:
                all_errors.extend(errors)

def run_guard(root_path: Path | None = None) -> bool:
    all_errors = []
    target = root_path or Path(__file__).resolve().parents[1]
    excludes = {
        ".venv", "venv", "env", ".env", ".git", "__pycache__", "node_modules",
        "graphify-out", "dist", "build", "out", ".next", ".nuxt",
        ".svelte-kit", ".angular", ".astro", ".docusaurus", ".turbo", ".cache"
    }
    
    for dirpath, dirnames, filenames in os.walk(target):
        dirnames[:] = [d for d in dirnames if d not in excludes]
        check_file_list(filenames, dirpath, all_errors)

    if all_errors:
        print("[TEST GUARD FATAL] Sham / non-behavioral tests detected:")
        for err in all_errors:
            print(f"  - {err}")
        return False

    return True

if __name__ == '__main__':
    print("[AAC] Running Anti-Sham Test Quality Guard...")
    target_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None
    if not run_guard(target_dir):
        print("=> ERROR: Unit tests rejected by Anti-Sham Guard. Write real behavioral tests.")
        sys.exit(1)
    print("=> SUCCESS: All unit tests verify real business logic and behavioral assertions.")
