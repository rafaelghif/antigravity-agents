#!/usr/bin/env python3
"""
DRY Guard (Anti-Duplication Engine): Detects copy-pasted and duplicate code blocks
across the repository using rolling window hashing. Inspired by jscpd & dry-deduplicator.
"""

import os
import sys
import re
import hashlib
import argparse
from pathlib import Path
from collections import defaultdict

SUPPORTED_EXTENSIONS = {".py", ".ts", ".js", ".tsx", ".jsx", ".go", ".java", ".rs", ".php"}

def clean_file_lines(filepath: Path) -> list:
    """Strips comments, blank lines, and whitespace while tracking original line numbers."""
    cleaned = []
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(("#", "//", "/*", "*", "<!--")):
                continue
            norm = re.sub(r'\s+', ' ', stripped)
            cleaned.append((norm, idx))
    except Exception as e:
        sys.stderr.write(f"DRY read notice for {filepath.name}: {e}\n")
    return cleaned

def extract_file_windows(filepath: Path, min_lines: int, hashes: dict) -> None:
    cleaned = clean_file_lines(filepath)
    if len(cleaned) < min_lines:
        return
    for i in range(len(cleaned) - min_lines + 1):
        window = cleaned[i : i + min_lines]
        chunk = "\n".join([w[0] for w in window])
        h = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
        start_line = window[0][1]
        end_line = window[-1][1]
        hashes[h].append((filepath, start_line, end_line, chunk))

def filter_distinct_locations(locs: list, min_lines: int, seen_combos: set) -> list:
    distinct = []
    for loc in locs:
        path, start, end, chunk = loc
        key = (str(path), start // min_lines)
        if key not in seen_combos:
            seen_combos.add(key)
            distinct.append(loc)
    return distinct

def detect_duplicates(file_list: list, min_lines: int = 6) -> list:
    hashes = defaultdict(list)
    for fpath in file_list:
        extract_file_windows(fpath, min_lines, hashes)

    results = []
    seen_combos = set()
    for h, locs in hashes.items():
        if len(locs) < 2:
            continue
        distinct_locs = filter_distinct_locations(locs, min_lines, seen_combos)
        if len(distinct_locs) >= 2:
            results.append({
                "hash": h,
                "lines_count": min_lines,
                "snippet": distinct_locs[0][3],
                "locations": [(loc[0], loc[1], loc[2]) for loc in distinct_locs]
            })
    return results

def process_filenames(dirpath: str, filenames: list, files: list) -> None:
    for f in filenames:
        ext = Path(f).suffix.lower()
        if ext in SUPPORTED_EXTENSIONS:
            files.append(Path(dirpath) / f)

def collect_repo_files(root_dir: Path) -> list:
    files = []
    excludes = {".git", ".venv", "venv", "node_modules", "__pycache__", "tests", "test", "build", "dist", ".agents", ".agents-backups"}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in excludes and not d.startswith(".agents-backups")]
        process_filenames(dirpath, filenames, files)
    return files

def analyze_workspace(root_dir: Path, min_lines: int = 6) -> list:
    files = collect_repo_files(root_dir)
    return detect_duplicates(files, min_lines)

def print_duplicate_locations(locations: list, root_path: Path) -> None:
    for loc in locations:
        rel_path = loc[0].relative_to(root_path) if loc[0].is_relative_to(root_path) else loc[0]
        print(f"  * {rel_path} (Lines {loc[1]}-{loc[2]})")

def report_duplicates(duplicates: list, root_path: Path) -> None:
    print(f"\n[DRY FATAL] Found {len(duplicates)} duplicate code block(s):")
    for i, dup in enumerate(duplicates, 1):
        print(f"\n--- [Duplicate #{i}] ({dup['lines_count']} lines) ---")
        print_duplicate_locations(dup['locations'], root_path)
        first_snippet_line = dup['snippet'].splitlines()[0] if dup['snippet'] else ""
        print(f"  Snippet start: \"{first_snippet_line}...\"")
        print("  -> Recommendation: Extract shared logic into a common helper, hook, or utility function.")

def main() -> None:
    parser = argparse.ArgumentParser(description="DRY Guard: Anti-Duplication Engine")
    parser.add_argument("path", nargs="?", default=".", help="Workspace path to inspect")
    parser.add_argument("--min-lines", type=int, default=6, help="Minimum consecutive identical lines to flag (default: 6)")
    parser.add_argument("--check", action="store_true", help="Exit with code 1 if duplicate code is detected")
    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    print(f"[AAC] Running DRY Anti-Duplication Guard (Min lines: {args.min_lines})...")
    duplicates = analyze_workspace(root_path, args.min_lines)

    if not duplicates:
        print("=> SUCCESS: Zero duplicate code blocks detected. Repository follows 100% DRY.")
        return

    report_duplicates(duplicates, root_path)

    if args.check:
        print("\n=> ERROR: DRY validation failed. Eliminate copy-paste duplication before proceeding.")
        sys.exit(1)

if __name__ == '__main__':
    main()
