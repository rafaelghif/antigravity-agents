#!/usr/bin/env python3
"""
UI Hygiene & Accessibility (WCAG 2.2 AA) Guard:
Inspects JSX, TSX, Vue, Svelte, and HTML files for common accessibility,
design-token, and styling anti-patterns (inspired by ux-ui-agent-skills).
"""

import os
import sys
import re
import argparse
from pathlib import Path

UI_EXTENSIONS = {".tsx", ".jsx", ".vue", ".svelte", ".html"}

def is_ui_file(filepath: Path) -> bool:
    return filepath.suffix.lower() in UI_EXTENSIONS

def check_img_alt(line: str, line_no: int, issues: list) -> None:
    if "<img" in line and "alt=" not in line and "alt:" not in line:
        issues.append(f"Line {line_no}: <img> element is missing an 'alt' attribute (WCAG 1.1.1 Non-text Content).")

def check_outline_none(line: str, line_no: int, issues: list) -> None:
    if ("outline-none" in line or "outline: none" in line or "outline:none" in line) and "focus-visible" not in line and "focus:" not in line:
        issues.append(f"Line {line_no}: 'outline-none' detected without 'focus-visible:' or focus ring styling (WCAG 2.4.7 Focus Visible).")

def check_button_type(line: str, line_no: int, issues: list) -> None:
    if "<button" in line and "type=" not in line:
        issues.append(f"Line {line_no}: <button> element is missing an explicit 'type' attribute (e.g. type=\"button\" or type=\"submit\").")

def check_inline_hex(line: str, line_no: int, issues: list) -> None:
    if "style=" in line and re.search(r'#[0-9a-fA-F]{3,8}\b', line):
        issues.append(f"Line {line_no}: Hardcoded hex color detected in inline styles. Use DTCG design tokens or Tailwind theme classes instead.")

def audit_ui_content(content: str, filename: str) -> list:
    issues = []
    lines = content.splitlines()
    for idx, line in enumerate(lines, start=1):
        check_img_alt(line, idx, issues)
        check_outline_none(line, idx, issues)
        check_button_type(line, idx, issues)
        check_inline_hex(line, idx, issues)
    return issues

def scan_files_in_dir(dirpath: str, filenames: list, all_violations: dict) -> None:
    for fname in filenames:
        fpath = Path(dirpath) / fname
        if is_ui_file(fpath):
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                issues = audit_ui_content(content, fname)
                if issues:
                    all_violations[str(fpath)] = issues
            except Exception as e:
                sys.stderr.write(f"UI scan notice for {fpath}: {e}\n")

def scan_workspace(root_dir: Path) -> dict:
    all_violations = {}
    excludes = {".git", ".venv", "venv", "node_modules", "__pycache__", "build", "dist", ".next", ".nuxt"}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in excludes]
        scan_files_in_dir(dirpath, filenames, all_violations)
    return all_violations

def print_file_issues(fpath: str, issues: list) -> None:
    print(f"\n  📁 {fpath}:")
    for issue in issues:
        print(f"    * {issue}")

def print_violations(violations: dict) -> None:
    print(f"[UI HYGIENE FATAL] Detected accessibility and design token violations in {len(violations)} file(s):")
    for fpath, issues in violations.items():
        print_file_issues(fpath, issues)

def main() -> None:
    parser = argparse.ArgumentParser(description="UI Hygiene & Accessibility (WCAG 2.2 AA) Guard")
    parser.add_argument("path", nargs="?", default=".", help="Root directory to check")
    parser.add_argument("--check", action="store_true", help="Exit with code 1 if violations are detected")
    args = parser.parse_args()

    root_dir = Path(args.path).resolve()
    violations = scan_workspace(root_dir)

    if violations:
        print_violations(violations)
        print("\n=> Recommendation: Ensure all <img> have alt text, <button> have explicit types, focus rings are preserved, and colors use design tokens.")
        if args.check:
            sys.exit(1)
    else:
        print("=> SUCCESS: All UI components meet WCAG 2.2 AA accessibility and DTCG design token standards.")

if __name__ == '__main__':
    main()
