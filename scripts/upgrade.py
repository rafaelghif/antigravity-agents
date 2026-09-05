#!/usr/bin/env python3
"""
AAC Upgrade Engine: Cross-platform upgrade launcher for Antigravity Agent Core.
Delegates to local install.py if present, or downloads and executes the upstream
bootstrap engine directly from GitHub with zero dependencies.
"""
from __future__ import annotations

import os
import re
import sys
import subprocess
import urllib.request
from pathlib import Path

UPSTREAM_INSTALLER_URL = "https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/install.py"

root_dir = Path(__file__).resolve().parents[1]
if (root_dir / "install.py").is_file():
    sys.path.insert(0, str(root_dir))
    from install import parse_semver, is_newer_version
else:
    def parse_semver(v_str: str) -> tuple[int, int, int]:
        m = re.match(r"^[^\d]*(\d+)\.(\d+)\.(\d+)", v_str)
        return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else (0, 0, 0)

    def is_newer_version(latest_str: str, current_str: str) -> bool:
        return parse_semver(latest_str) > parse_semver(current_str)

def main() -> None:
    root_dir = Path(__file__).resolve().parents[1]
    local_installer = root_dir / "install.py"

    sub_env = os.environ.copy()
    sub_env["PYTHONIOENCODING"] = "utf-8"
    sub_env["PYTHONUTF8"] = "1"

    if local_installer.is_file():
        cmd = [sys.executable, str(local_installer)] + sys.argv[1:]
        sys.exit(subprocess.call(cmd, cwd=root_dir, env=sub_env))

    print("=> Local install.py not found in consumer workspace. Fetching upstream installer engine...")
    try:
        req = urllib.request.Request(
            UPSTREAM_INSTALLER_URL,
            headers={"User-Agent": "AAC-Upgrader"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            script_code = resp.read().decode("utf-8")
        
        proc = subprocess.run([sys.executable, "-c", script_code] + sys.argv[1:], cwd=root_dir, env=sub_env)
        sys.exit(proc.returncode)
    except Exception as exc:
        sys.stderr.write(f"Upgrade failed: {exc}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
