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
CORE_AGENT_PATHS = (
    "AGENTS.md",
    "GEMINI.md",
    ".agents/config.json",
    ".agents/TASK_TEMPLATE.md",
    ".agents/mcp_config.json.example",
    ".agents/antigravity-settings.example.json",
    ".agents/antigravity-compatibility.json",
    ".agents/agents/planner.md",
    ".agents/agents/implementer.md",
    ".agents/agents/reviewer.md",
    ".agents/agents/security-reviewer.md",
    ".agents/skills/code-quality/SKILL.md",
    ".agents/skills/verification/SKILL.md",
    ".agents/skills/security/SKILL.md",
    ".agents/skills/architecture/SKILL.md",
    ".agents/skills/design/SKILL.md",
    ".agents/skills/semantic-graphing/SKILL.md",
    ".agents/skills/dry/SKILL.md",
    "scripts/validate.py",
    "scripts/verify.py",
    "scripts/test_quality_guard.py",
    "scripts/dry_guard.py",
    "scripts/git_hygiene_guard.py",
    "scripts/upgrade.py",
    "scripts/ui_hygiene_guard.py",
    "scripts/self_learner.py",
    "scripts/memory_consolidator.py",
)

REQUIRED_PATHS = CORE_AGENT_PATHS + ("scripts/semantic_grapher.py",)
CONSUMER_REQUIRED_PATHS = CORE_AGENT_PATHS

OPTIONAL_PATHS = (
    ".agents/brain/soul.md",
    ".agents/brain/rules.md",
    ".agents/brain/memory.md",
    ".agents/brain/active_context.md",
    ".agents/brain/ANCHOR.md",
    ".agents/brain/schema.md",
    ".agents/brain/env-required.json",
    ".agents/common/utils.md",
)


def is_framework_repo() -> bool:
    """Check if running directly inside the upstream AAC framework repository."""
    install_sh = ROOT / "install.sh"
    if install_sh.is_file():
        try:
            content = install_sh.read_text(encoding="utf-8")
            if "antigravity-agents.git" in content:
                return True
        except (OSError, UnicodeDecodeError) as exc:
            sys.stderr.write(f"Notice: Failed to read install.sh: {exc}\n")
    return False


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(relative_path: str) -> dict:
    path = ROOT / relative_path
    if relative_path in OPTIONAL_PATHS and not path.exists():
        return {}
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


def validate_markdown_metadata(directory: str, expected_count: int, required_fields: tuple[str, ...], pattern: str = "*.md") -> None:
    files = sorted((ROOT / directory).glob(pattern))
    if len(files) < expected_count:
        fail(f"expected at least {expected_count} files in {directory}, found {len(files)}")
    for path in files:
        content = path.read_text(encoding="utf-8")
        match = re.match(r"^---\n(?P<frontmatter>.*?)\n---\n", content, re.DOTALL)
        if not match:
            fail(f"{path.relative_to(ROOT)} is missing YAML frontmatter")
        frontmatter = match.group("frontmatter")
        missing = [f for f in required_fields if not re.search(rf"^{f}:\s*\S+", frontmatter, re.MULTILINE)]
        if missing:
            fail(f"{path.relative_to(ROOT)} is missing frontmatter: {', '.join(missing)}")
        if len(content.split()) > 700:
            fail(f"{path.relative_to(ROOT)} exceeds the 700-word instruction budget")


def validate_instruction_budget() -> None:
    if not is_framework_repo():
        # In consumer projects, do not fail on custom project instructions in AGENTS.md / GEMINI.md
        return
    for relative_path, maximum in (("AGENTS.md", 600), ("GEMINI.md", 80), (".agents/TASK_TEMPLATE.md", 500)):
        words = (ROOT / relative_path).read_text(encoding="utf-8").split()
        if len(words) > maximum:
            fail(f"{relative_path} exceeds the {maximum}-word always-on budget")
    bootstrap = (ROOT / "GEMINI.md").read_text(encoding="utf-8")
    if "AGENTS.md" not in bootstrap:
        fail("GEMINI.md must bootstrap AGENTS.md")


def validate_settings() -> None:
    settings = load_json(".agents/antigravity-settings.example.json")
    required = {
        "toolPermission": "always-proceed",
        "enableTerminalSandbox": False,
        "allowNonWorkspaceAccess": True,
    }
    for key, expected in required.items():
        if settings.get(key) != expected:
            fail(f"settings baseline must set {key}={expected!r}")
    permissions = settings.get("permissions")
    if not isinstance(permissions, dict):
        fail("settings baseline must define permissions")
    for key in ("allow", "deny"):
        if not isinstance(permissions.get(key), list) or not permissions[key]:
            fail(f"settings permissions.{key} must be a non-empty list")
    if not any(item.startswith("command(") for item in permissions["deny"]):
        fail("settings baseline must deny at least one command")


def validate_compatibility() -> None:
    compatibility = load_json(".agents/antigravity-compatibility.json")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(compatibility.get("cli_version"))):
        fail("compatibility cli_version must be semantic version text")
    if not compatibility.get("official_docs") or not all(
        str(url).startswith("https://antigravity.google/docs/")
        for url in compatibility["official_docs"]
    ):
        fail("compatibility must list official Antigravity documentation URLs")


def validate_recovery_state() -> None:
    plans = sorted((ROOT / ".agents/plans").glob("*.md"))
    if not plans:
        return
    if len(plans) != 1:
        fail(f"expected exactly one active plan, found {len(plans)}")
    content = plans[0].read_text(encoding="utf-8")
    if "status: COMPLETE" in content:
        fail("active plan cannot be marked COMPLETE")
    if not re.search(r"- \[ \]", content):
        fail("active plan must contain an unchecked delivery task")
    for forbidden in (".agents/brain/state.json", ".agents/brain/mcp-registry.json"):
        if (ROOT / forbidden).exists():
            fail(f"forbidden legacy state file exists: {forbidden}")


def validate_scanner_applicability() -> None:
    security = load_json(".agents/config.json")["security"]
    applicability = security.get("scanner_applicability")
    if not isinstance(applicability, dict):
        fail("security scanner_applicability is required")
    declared = set(security.get("sast_tools", [])) | set(security.get("secret_scanning", []))
    configured = set(applicability.get("repository", [])) | set(applicability.get("language_specific", []))
    if not configured <= declared:
        fail("scanner applicability contains undeclared tools")
    if not isinstance(applicability.get("dependency", []), list):
        fail("scanner applicability dependency must be a list")
    if not applicability.get("not_applicable_reason"):
        fail("scanner applicability needs a not-applicable reason")


def validate_manifest() -> None:
    required = REQUIRED_PATHS if is_framework_repo() else CONSUMER_REQUIRED_PATHS
    for relative_path in required:
        if not (ROOT / relative_path).is_file():
            fail(f"missing required file: {relative_path}")


def validate_version() -> None:
    config = load_json(".agents/config.json")
    version = config.get("core_version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail("config.json core_version must be semantic version text")
    if not is_framework_repo():
        # Consumer project: do not lock consumer's README.md, CHANGELOG.md, install.sh to AAC version
        return
    markers = {
        "AGENTS.md": f"AAC v{version}",
        "README.md": f"version-{version}",
        "install.sh": f' AAC_REF="v{version}"',
        "install.ps1": f'$AacRef = "v{version}"',
        ".agents/TASK_TEMPLATE.md": f"AAC v{version}",
        ".github/workflows/agent-gates.yml": f"AAC v{version}",
    }
    for relative_path, marker in markers.items():
        content = (ROOT / relative_path).read_text(encoding="utf-8")
        if marker not in content:
            fail(f"{relative_path} does not contain version marker {marker}")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## [{version}]" not in changelog:
        fail(f"CHANGELOG.md does not contain release heading [{version}]")


def main() -> int:
    try:
        validate_manifest()
        load_json(".agents/config.json")
        load_json(".agents/brain/env-required.json")
        load_json(".agents/antigravity-compatibility.json")
        validate_mcp()
        validate_markdown_metadata(".agents/skills", 10, ("name", "description"), "*/SKILL.md")
        validate_markdown_metadata(".agents/agents", 5, ("name", "description", "mode"))
        validate_instruction_budget()
        validate_settings()
        validate_compatibility()
        validate_recovery_state()
        validate_scanner_applicability()
        validate_version()
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 1
    print("AAC Antigravity structural validation: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
