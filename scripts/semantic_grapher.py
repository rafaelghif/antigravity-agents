#!/usr/bin/env python3
"""
Semantic Grapher: Extracts classes, functions, and method signatures to build a semantic map of the repository.
This allows agents to understand architecture without reading the full files.
"""

import ast
import os
import re
import sys
from pathlib import Path


def print_class_methods(class_node):
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef):
            args = [a.arg for a in item.args.args]
            print(f"    def {item.name}({', '.join(args)})")

def parse_python(filepath: Path):
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        print(f"\n[FILE] {filepath}")
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                print(f"  class {node.name}:")
                print_class_methods(node)
            elif isinstance(node, ast.FunctionDef):
                args = [a.arg for a in node.args.args]
                print(f"  def {node.name}({', '.join(args)})")
    except Exception as e:
        print(f"\n[FILE] {filepath} (Error parsing AST: {e})")

def parse_regex(filepath: Path, lang: str):
    try:
        content = filepath.read_text(encoding="utf-8")
        print(f"\n[FILE] {filepath}")
        
        if lang in ["ts", "js"]:
            classes = re.findall(r'class\s+([A-Za-z0-9_]+)', content)
            functions = re.findall(r'(?:function\s+|const\s+|let\s+)([A-Za-z0-9_]+)\s*(?:=|:)?\s*(?:\([^)]*\)\s*=>|\([^)]*\)\s*\{)', content)
            for c in classes:
                print(f"  class {c}")
            for f in functions:
                print(f"  func/arrow {f}")
        elif lang == "go":
            structs = re.findall(r'type\s+([A-Za-z0-9_]+)\s+struct', content)
            functions = re.findall(r'func\s+(?:\([^)]+\)\s+)?([A-Za-z0-9_]+)\s*\(', content)
            for s in structs:
                print(f"  struct {s}")
            for f in functions:
                print(f"  func {f}")
    except Exception as e:
        print(f"\n[FILE] {filepath} (Error parsing: {e})")

def process_files_for_ext(dirpath, filenames, ext):
    for filename in filenames:
        if filename.endswith(ext):
            filepath = Path(dirpath) / filename
            if ext == ".py":
                parse_python(filepath)
            else:
                parse_regex(filepath, ext[1:])

def process_extension(root_dir: Path, ext: str):
    excludes = {"node_modules", ".venv", ".git"}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in excludes]
        process_files_for_ext(dirpath, filenames, ext)

def scan_directory(root_dir: Path):
    print(f"Semantic Graph for {root_dir}\n" + "="*40)
    for ext in [".py", ".ts", ".js", ".go"]:
        process_extension(root_dir, ext)

if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    scan_directory(target)
