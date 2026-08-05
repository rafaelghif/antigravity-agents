#!/usr/bin/env python3
"""Validate AAC's Antigravity workspace contracts without third-party packages."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION_FILES = (
    "AGENTS.md",
    "README.md",
    "install.sh",
    "install.ps1",
    ".agents/TASK_TEMPLATE.md",
    ".github/workflows/agent-gates.yml",
)
REQUIRED_PATHS = (
    "AGENTS.md",
    ".agents/config.json",
    ".agents/TASK_TEMPLATE.md",
    ".agents/brain/soul.md",
    ".agents/brain/rules.md",
    ".agents/brain/schema.md",
    ".agents/brain/env-required.json",
    ".agents/common/utils.md",
    ".agents/mcp_config.json.example",
    ".agents/antigravity-settings.example.json",
    ".agents/skills/code-engineer.md",
    ".agents/skills/devops-manager.md",
    ".agents/skills/quality-assurance.md",
    ".agents/skills/security-docs-auditor.md",
    ".agents/skills/system-architect.md",
    ".agents/skills/system-janitor.md",
)


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(relative_path: str) -> dict:
    path = ROOT / relative_path
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON in {relative_path}: {exc}")
    if not isinstance(value, dict):
        fail(f"{relative_path} must contain a JSON object")
    return value


def validate_mcp() -> None:
    config = load_json(".agents/mcp_config.json.example")
    servers = config.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        fail("MCP example must define mcpServers")
    for name, server in servers.items():
        if not isinstance(server, dict):
            fail(f"MCP server {name} must be an object")
        if "serverURL" in server:
            fail(f"MCP server {name} uses deprecated serverURL; use serverUrl")
        if "serverUrl" not in server and "command" not in server:
            fail(f"MCP server {name} needs serverUrl or command")
        if server.get("serverUrl") and not str(server["serverUrl"]).startswith("https://"):
            fail(f"remote MCP server {name} must use HTTPS")
        args = server.get("args", [])
        if not isinstance(args, list) or any(not isinstance(item, str) for item in args):
            fail(f"MCP server {name} args must be an array of strings")
        if any(item.endswith(":latest") for item in args):
            fail(f"MCP server {name} uses mutable :latest image")


def validate_skills() -> None:
    skills_dir = ROOT / ".agents/skills"
    skill_files = sorted(skills_dir.glob("*.md"))
    if len(skill_files) != 6:
        fail(f"expected 6 flat workspace skills, found {len(skill_files)}")
    if list(skills_dir.glob("*/SKILL.md")):
        fail("nested SKILL.md files are not supported; use .agents/skills/<name>.md")
    for path in skill_files:
        content = path.read_text(encoding="utf-8")
        match = re.match(r"^---\n(?P<frontmatter>.*?)\n---\n", content, re.DOTALL)
        if not match:
            fail(f"{path.relative_to(ROOT)} is missing YAML frontmatter")
        frontmatter = match.group("frontmatter")
        if not re.search(r"^name:\s*\S+", frontmatter, re.MULTILINE):
            fail(f"{path.relative_to(ROOT)} is missing frontmatter name")
        if not re.search(r"^description:\s*\S+", frontmatter, re.MULTILINE):
            fail(f"{path.relative_to(ROOT)} is missing frontmatter description")


def validate_manifest() -> None:
    for relative_path in REQUIRED_PATHS:
        if not (ROOT / relative_path).is_file():
            fail(f"missing required file: {relative_path}")


def validate_version() -> None:
    config = load_json(".agents/config.json")
    version = config.get("core_version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail("config.json core_version must be semantic version text")
    for relative_path in VERSION_FILES:
        content = (ROOT / relative_path).read_text(encoding="utf-8")
        if version not in content:
            fail(f"{relative_path} does not contain core version {version}")
    stale = re.compile(r"(?:V|v)?4\.3\.[012]")
    for relative_path in VERSION_FILES:
        content = (ROOT / relative_path).read_text(encoding="utf-8")
        if stale.search(content.replace(version, "")):
            fail(f"{relative_path} contains a stale 4.3.x version")


def main() -> int:
    try:
        validate_manifest()
        load_json(".agents/config.json")
        load_json(".agents/brain/env-required.json")
        validate_mcp()
        validate_skills()
        validate_version()
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 1
    print("AAC Antigravity structural validation: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
