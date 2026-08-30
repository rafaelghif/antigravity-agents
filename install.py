#!/usr/bin/env python3
"""
AAC Upgrade Engine: One-command effortless upgrading of Antigravity Agent Core.
Auto-discovers the latest GitHub release, preserves memories/rules, updates files,
and validates the upgraded workspace.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

GITHUB_API_URL = "https://api.github.com/repos/rafaelghif/antigravity-agents/releases/latest"
REMOTE_REPO = "https://github.com/rafaelghif/antigravity-agents.git"


def parse_semver(v_str: str) -> tuple[int, int, int]:
    clean = re.sub(r"^[^\d]*", "", v_str)
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", clean)
    if match:
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return (0, 0, 0)


def is_newer_version(latest_str: str, current_str: str) -> bool:
    return parse_semver(latest_str) > parse_semver(current_str)


def get_current_version(root_dir: Path) -> str:
    config_path = root_dir / ".agents" / "config.json"
    if config_path.is_file():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            return data.get("core_version", "0.0.0")
        except (OSError, json.JSONDecodeError) as exc:
            sys.stderr.write(f"Config read notice: {exc}\n")
    return "0.0.0"


def get_latest_github_release(current_ver: str) -> tuple[str, str, str]:
    curl_bin = shutil.which("curl") or "curl"
    try:
        res = subprocess.run(
            [curl_bin, "-s", "-H", "User-Agent: AAC-Upgrader", GITHUB_API_URL],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=8,
        )
        if res.returncode == 0 and res.stdout:
            data = json.loads(res.stdout)
            tag = data.get("tag_name", "")
            title = data.get("name", tag)
            body = data.get("body", "")
            if tag:
                return (tag, title, body)
    except Exception as exc:
        sys.stderr.write(f"GitHub API release notice: {exc}\n")

    try:
        res = subprocess.run(
            ["git", "ls-remote", "--tags", "--refs", REMOTE_REPO],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=8,
        )
        if res.returncode == 0:
            tags = [line.split("/")[-1] for line in res.stdout.splitlines() if line.strip()]
            valid_tags = [t for t in tags if re.match(r"^v?\d+\.\d+\.\d+$", t)]
            if valid_tags:
                sorted_tags = sorted(valid_tags, key=parse_semver)
                latest_tag = sorted_tags[-1]
                return (latest_tag, latest_tag, "Upstream release from Git tags.")
    except Exception as exc:
        sys.stderr.write(f"Git remote tags notice: {exc}\n")

    fallback_tag = f"v{current_ver}" if current_ver != "0.0.0" else "v4.30.0"
    return (fallback_tag, fallback_tag, "Fallback version.")


def check_update_status(root_dir: Path) -> dict[str, object]:
    current = get_current_version(root_dir)
    latest_tag, title, notes = get_latest_github_release(current)
    has_update = is_newer_version(latest_tag, current)
    return {
        "current_version": current,
        "latest_version": latest_tag,
        "title": title,
        "notes": notes,
        "has_update": has_update,
    }


def find_powershell_binary() -> str:
    for candidate in ("pwsh", "powershell", "powershell.exe"):
        found = shutil.which(candidate)
        if found:
            return found
    return "powershell"


def run_upgrade(root_dir: Path, target_version: str) -> bool:
    print(f"\n=> Downloading and installing AAC {target_version}...")
    is_windows = sys.platform.startswith("win")
    script_name = "install.ps1" if is_windows else "install.sh"
    install_url = f"https://raw.githubusercontent.com/rafaelghif/antigravity-agents/{target_version}/{script_name}"

    tmp_path: Path | None = None
    try:
        suffix = ".ps1" if is_windows else ".sh"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)

        curl_bin = shutil.which("curl") or "curl"
        dl_res = subprocess.run(
            [curl_bin, "-fsSL", install_url, "-o", str(tmp_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15,
        )
        if dl_res.returncode != 0:
            print("=> Download failed: unable to fetch installer script.")
            return False

        env = {
            **os.environ,
            "AAC_TARGET_DIR": str(root_dir),
            "AAC_REF": target_version,
        }

        if is_windows:
            ps_bin = find_powershell_binary()
            cmd = [ps_bin, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(tmp_path)]
        else:
            bash_bin = shutil.which("bash") or "bash"
            cmd = [bash_bin, str(tmp_path)]

        exec_res = subprocess.run(cmd, cwd=root_dir, env=env)
        return exec_res.returncode == 0
    except Exception as exc:
        print(f"=> ERROR running upgrade: {exc}")
        return False
    finally:
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError as err:
                sys.stderr.write(f"Notice: unable to remove temporary file {tmp_path}: {err}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="AAC Installer Engine: Auto-bootstrap the world-class L9 agent workspace")
    parser.add_argument("path", nargs="?", default=".", help="Project workspace root")
    parser.add_argument("--check", action="store_true", help="Check for latest version without installing")
    parser.add_argument("--force", action="store_true", help="Force re-installation")
    args = parser.parse_args()

    root_dir = Path(args.path).resolve()
    status = check_update_status(root_dir)

    print("=" * 60)
    print("🚀 Antigravity Agent Core (AAC) Installer")
    print("=" * 60)
    print(f"Current Workspace Version: v{status['current_version']}")
    print(f"Latest Upstream Release:   {status['latest_version']}")

    if not status["has_update"] and not args.force and status["current_version"] != "0.0.0":
        print("\n✨ You are already running the latest world-class AAC agent!")
        return

    if status["has_update"] or status["current_version"] == "0.0.0":
        action = "Update" if status["current_version"] != "0.0.0" else "Install"
        print(f"\n🎉 Latest {action} Available: {status['latest_version']} ({status['title']})")
        print("\n--- Release Notes Highlight ---")
        first_lines = "\n".join(str(status["notes"]).splitlines()[:10])
        print(first_lines)
        print("-------------------------------")

    if args.check:
        print("\nRun 'python3 install.py' to apply this configuration effortlessly.")
        return

    success = run_upgrade(root_dir, str(status["latest_version"]))
    if success:
        print("\n" + "=" * 60)
        print(f"✅ AAC successfully configured to {status['latest_version']}!")
        print("💡 All custom memories (.agents/brain/memory.md) and rules were preserved.")
        print("=" * 60)
        verify_script = root_dir / "scripts" / "verify.py"
        if verify_script.is_file():
            print("\n=> Running post-install verification gates...")
            subprocess.run([sys.executable, str(verify_script), "--execute", "--terse"], cwd=root_dir)
    else:
        print("\n❌ Installation failed. Check logs above or rollback with .agents-backups/.")
        sys.exit(1)


if __name__ == "__main__":
    main()
