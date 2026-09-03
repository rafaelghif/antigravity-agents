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
        if shutil.which("pytest"):
            checks.append(("test", "python", "pytest"))
        elif (ROOT / "tests").is_dir():
            checks.append(("test", "python", f'"{sys.executable}" -m unittest discover tests'))
    elif (ROOT / "tests").is_dir():
        checks.append(("test", "python", f'"{sys.executable}" -m unittest discover tests'))
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
    parser.add_argument("--release", action="store_true", help="Enforce production release gate: requires .agents/brain/AITL_CONSENSUS.yaml approval")
    args = parser.parse_args()

    if args.release:
        aitl_file = ROOT / ".agents" / "brain" / "AITL_CONSENSUS.yaml"
        if not aitl_file.is_file():
            print("=> FATAL: Production release gate failed! .agents/brain/AITL_CONSENSUS.yaml is missing.")
            return 1
        try:
            aitl_text = aitl_file.read_text(encoding="utf-8")
            if "STATUS: APPROVED" not in aitl_text:
                print("=> FATAL: Production release gate failed! AITL_CONSENSUS.yaml does not have STATUS: APPROVED.")
                return 1
            if not args.terse:
                print("✅ AITL Consensus Verified (.agents/brain/AITL_CONSENSUS.yaml: APPROVED)")
        except Exception as e:
            print(f"=> FATAL: Error reading AITL_CONSENSUS.yaml: {e}")
            return 1

    # L9 Hard Boundaries for Agent Compliance are now handled by intent_guard.py
    checks = detect()
    
    script_checks = [
        ("intent_guard.py", "intent_lifecycle_check", "", True),
        ("validate.py", "validate", "", False),
        ("complexity_analyzer.py", "complexity_check", "", False),
        ("test_quality_guard.py", "anti_sham_check", "", False),
        ("dry_guard.py", "dry_check", "--check", False),
        ("git_hygiene_guard.py", "git_hygiene_check", "--check", False),
        ("ui_hygiene_guard.py", "ui_hygiene_check", "--check", False),
    ]

    for script, check_name, extra_args, at_start in script_checks:
        script_path = ROOT / "scripts" / script
        if script_path.is_file():
            cmd = f'"{sys.executable}" scripts/{script}'
            if extra_args:
                cmd += f" {extra_args}"
            item = (check_name, "AAC", cmd)
            if at_start:
                checks.insert(0, item)
            else:
                checks.append(item)

    neuro_engine = ROOT / "scripts" / "neurosymbolic_engine.py"
    if neuro_engine.is_file():
        if not (ROOT / "handoff.json").is_file():
            print("=> FATAL: handoff.json is missing! Rule [HANDOFF_CONTRACTS] violated. Subagents must deliver a structured handoff payload.")
            return 1
        checks.append(("neurosymbolic_validation", "AAC", f'"{sys.executable}" scripts/neurosymbolic_engine.py handoff.json'))
        
    if not checks:
        if not args.terse:
            print("- application stack: not detected")
            print("- project tests/formatters/linters: not available")
        return 0

    if not args.terse:
        print("Stack detection:")
        for name, stack, run in checks:
            status = "available" if shutil.which(shlex.split(run)[0]) else "not available"
            print(f"- {stack} {name}: {run} ({status})")

    exit_code = 0
    passed_count = 0
    for name, stack, run in checks:
        status = "available" if shutil.which(shlex.split(run)[0]) else "not available"
        if args.execute and status == "available":
            if not args.terse:
                print(f"\n=> Executing {stack} {name}...")
                result = subprocess.run(shlex.split(run), cwd=ROOT, timeout=300)
            else:
                result = subprocess.run(shlex.split(run), cwd=ROOT, capture_output=True, text=True, timeout=300)
            
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
