#!/usr/bin/env python3
"""
Git Hygiene Guard: Detects, blocks, and purges temporary/scratch scripts,
debug artifacts, and trash files from polluting Git commits and the repository.
"""

import os
import sys
import re
import subprocess
import argparse
from pathlib import Path

SCRATCH_PATTERNS = [
    r'^scratch(_.*)?\.(py|sh|js|ts|txt|md|json)$',
    r'.*_scratch\.(py|sh|js|ts|txt|md|json)$',
    r'^tmp(_.*)?\.(py|sh|js|ts|txt|md|json)$',
    r'.*_tmp\.(py|sh|js|ts|txt|md|json)$',
    r'^temp(_.*)?\.(py|sh|js|ts|txt|md|json)$',
    r'.*_temp\.(py|sh|js|ts|txt|md|json)$',
    r'^debug(_.*)?\.(py|sh|js|ts|txt|md|json)$',
    r'.*_debug\.(py|sh|js|ts|txt|md|json)$',
    r'^poc(_.*)?\.(py|sh|js|ts|txt|md|json)$',
    r'.*_poc\.(py|sh|js|ts|txt|md|json)$',
    r'^test_scratch(_.*)?\.(py|sh|js|ts|txt|md|json)$',
    r'^test_temp(_.*)?\.(py|sh|js|ts|txt|md|json)$',
    r'.*\.(tmp|bak|swp)$',
    r'^release_notes_.*\.txt$',
]

def is_scratch_file(filepath: Path) -> bool:
    name = filepath.name.lower()
    path_str = filepath.as_posix().lower()

    if name == ".gitkeep" or name.startswith(".git"):
        return False

    if ".agents/scratch" in path_str and name != ".gitkeep":
        return True

    for pattern in SCRATCH_PATTERNS:
        if re.search(pattern, name):
            return True
    return False

def check_file_list(dirpath: str, filenames: list, scratch_files: list) -> None:
    for f in filenames:
        fpath = Path(dirpath) / f
        if is_scratch_file(fpath):
            scratch_files.append(fpath)

def find_scratch_files(root_dir: Path) -> list:
    scratch_files = []
    excludes = {".git", ".venv", "venv", "node_modules", "__pycache__", "build", "dist"}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in excludes]
        check_file_list(dirpath, filenames, scratch_files)
    return scratch_files

def clean_scratch_files(root_dir: Path) -> list:
    scratch_files = find_scratch_files(root_dir)
    removed = []
    for fpath in scratch_files:
        try:
            if fpath.is_file() or fpath.is_symlink():
                fpath.unlink()
                removed.append(fpath)
        except Exception as e:
            sys.stderr.write(f"Git hygiene clean notice: {e}\n")
    return removed

def check_staged_git_files(root_dir: Path) -> list:
    try:
        res = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=root_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60
        )
        if res.returncode == 0:
            lines = res.stdout.splitlines()
            return [Path(line) for line in lines if is_scratch_file(Path(line))]
    except Exception as e:
        sys.stderr.write(f"Git diff notice: {e}\n")
    return []

def main() -> None:
    parser = argparse.ArgumentParser(description="Git Hygiene Guard: Prevent scratch/trash artifacts in Git")
    parser.add_argument("path", nargs="?", default=".", help="Root directory to check")
    parser.add_argument("--check", action="store_true", help="Check working tree and git staging, exit 1 if scratch files found")
    parser.add_argument("--clean", action="store_true", help="Automatically delete detected scratch files")
    args = parser.parse_args()

    root_dir = Path(args.path).resolve()

    if args.clean:
        removed = clean_scratch_files(root_dir)
        if removed:
            print(f"[AAC] Cleaned {len(removed)} scratch/trash file(s):")
            for r in removed:
                print(f"  - Deleted: {r}")
        else:
            print("[AAC] Workspace is clean. Zero scratch files found.")
        return

    staged_scratch = check_staged_git_files(root_dir)
    workspace_scratch = find_scratch_files(root_dir)

    all_violations = list(set([str(p) for p in (staged_scratch + workspace_scratch)]))

    if all_violations:
        print("[HYGIENE FATAL] Detected scratch/throwaway files in workspace or Git staging:")
        for v in all_violations:
            print(f"  * {v}")
        print("\n=> Recommendation: Delete scratch scripts or run `python3 scripts/git_hygiene_guard.py --clean` before committing.")
        if args.check:
            sys.exit(1)
    else:
        print("=> SUCCESS: Workspace and Git staging meet 100% Git hygiene standards.")

if __name__ == '__main__':
    main()
