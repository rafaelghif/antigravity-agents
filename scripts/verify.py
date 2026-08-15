#!/usr/bin/env python3
"""Detect a repository stack and print safe verification commands."""

from __future__ import annotations

import json
import shutil
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
    print("Stack detection:")
    checks = detect()
    if not checks:
        print("- application stack: not detected")
        print("- project tests/formatters/linters: not available")
    else:
        for name, stack, run in checks:
            status = "available" if shutil.which(run.split()[0]) else "not available"
            print(f"- {stack} {name}: {run} ({status})")
    structural = ROOT / "scripts" / "validate.py"
    if structural.is_file():
        print("- AAC structural validation: python3 scripts/validate.py (available)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
