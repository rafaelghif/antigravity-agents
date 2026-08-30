#!/usr/bin/env python3
"""Detect a repository stack and print or execute safe verification commands."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import shlex
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def command(*parts: str) -> str:
    return " ".join(parts)


def detect() -> list[tuple[str, str, str]]:
    checks: list[tuple[str, str, str]] = []
    if (ROOT / "package.json").is_file():
        try:
            data = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
            scripts = data.get("scripts") or {}
        except (json.JSONDecodeError, AttributeError, TypeError):
            scripts = {}
        manager = "npm"
        if (ROOT / "pnpm-lock.yaml").is_file():
            manager = "pnpm"
        elif (ROOT / "yarn.lock").is_file():
            manager = "yarn"
        for name in ("format", "lint", "typecheck", "test", "build"):
            if name in scripts:
                checks.append((name, manager, command(manager, "run", name)))
    if (ROOT / "pyproject.toml").is_file() or (ROOT / "pytest.ini").is_file():
        checks.append(("test", "python", "pytest"))
    if (ROOT / "Cargo.toml").is_file():
        checks.append(("test", "rust", "cargo test"))
    if (ROOT / "go.mod").is_file():
        checks.append(("test", "go", "go test ./..."))
    if (ROOT / "composer.json").is_file():
        checks.append(("test", "php", "composer test"))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect a repository stack and print or execute safe verification commands.")
    parser.add_argument("--execute", action="store_true", help="Execute the detected commands")
    parser.add_argument("--terse", "-q", action="store_true", help="ACI Mode: output minimal telegraphic summary")
    args = parser.parse_args()

    # L9 Hard Boundaries for Agent Compliance
    if not (ROOT / "intent.yaml").is_file():
        print("=> FATAL: intent.yaml is missing! Vibe coding is forbidden. Rule [INTENT_ARCHITECTURE] violated.")
        return 1
    if not (ROOT / "tasks").is_dir() or not any((ROOT / "tasks").iterdir()):
        print("=> FATAL: tasks/ directory is missing or empty! Rule [MICRO_TASK_SPLIT] violated.")
        return 1

    checks = detect()
    structural = ROOT / "scripts" / "validate.py"
    if structural.is_file():
        checks.append(("validate", "AAC", "python3 scripts/validate.py"))
        
    complexity = ROOT / "scripts" / "complexity_analyzer.py"
    if complexity.is_file():
        checks.append(("complexity_check", "AAC", "python3 scripts/complexity_analyzer.py"))

    test_guard = ROOT / "scripts" / "test_quality_guard.py"
    if test_guard.is_file():
        checks.append(("anti_sham_check", "AAC", "python3 scripts/test_quality_guard.py"))

    dry_guard = ROOT / "scripts" / "dry_guard.py"
    if dry_guard.is_file():
        checks.append(("dry_check", "AAC", "python3 scripts/dry_guard.py --check"))

    hygiene_guard = ROOT / "scripts" / "git_hygiene_guard.py"
    if hygiene_guard.is_file():
        checks.append(("git_hygiene_check", "AAC", "python3 scripts/git_hygiene_guard.py --check"))

    ui_guard = ROOT / "scripts" / "ui_hygiene_guard.py"
    if ui_guard.is_file():
        checks.append(("ui_hygiene_check", "AAC", "python3 scripts/ui_hygiene_guard.py --check"))

    neuro_engine = ROOT / "scripts" / "neurosymbolic_engine.py"
    if neuro_engine.is_file():
        if not (ROOT / "handoff.json").is_file():
            print("=> FATAL: handoff.json is missing! Rule [HANDOFF_CONTRACTS] violated. Subagents must deliver a structured handoff payload.")
            return 1
        checks.append(("neurosymbolic_validation", "AAC", "python3 scripts/neurosymbolic_engine.py handoff.json"))
        
    if not checks:
        if not args.terse:
            print("- application stack: not detected")
            print("- project tests/formatters/linters: not available")
        return 0

    if not args.terse:
        print("Stack detection:")
        for name, stack, run in checks:
            status = "available" if shutil.which(run.split()[0]) else "not available"
            print(f"- {stack} {name}: {run} ({status})")

    exit_code = 0
    passed_count = 0
    for name, stack, run in checks:
        status = "available" if shutil.which(run.split()[0]) else "not available"
        if args.execute and status == "available":
            if not args.terse:
                print(f"\n=> Executing {stack} {name}...")
                result = subprocess.run(shlex.split(run), cwd=ROOT)
            else:
                result = subprocess.run(shlex.split(run), cwd=ROOT, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"=> ERROR: {stack} {name} failed with exit code {result.returncode}")
                if args.terse and result.stderr:
                    print(result.stderr.strip())
                elif args.terse and result.stdout:
                    print(result.stdout.strip())
                exit_code = result.returncode
            else:
                passed_count += 1
                if not args.terse:
                    print(f"=> SUCCESS: {stack} {name} passed.")

    if args.terse and exit_code == 0:
        print(f"=> ACI VERIFY: OK ({passed_count}/{len(checks)} gates passed).")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
