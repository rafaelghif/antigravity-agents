#!/usr/bin/env python3
"""Validate AAC's Antigravity workspace contracts without third-party packages."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
VERSION_FILES = (
    "AGENTS.md",
    "README.md",
    "install.sh",
    "install.ps1",
    ".agents/TASK_TEMPLATE.md",
)
CORE_AGENT_PATHS = (
    "AGENTS.md",
    "GEMINI.md",
    "agent.md",
    ".agents/config.json",
    ".agents/TASK_TEMPLATE.md",
    ".agents/mcp_config.json.example",
    ".agents/antigravity-settings.example.json",
    ".agents/antigravity-compatibility.json",
    ".agents/rules/01-grounding.md",
    ".agents/rules/02-project-adaptation.md",
    ".agents/rules/03-token-economy.md",
    ".agents/rules/04-verification-gates.md",
    ".agents/rules/05-git-hygiene.md",
    ".agents/agents/scrum-master.md",
    ".agents/agents/product-manager.md",
    ".agents/agents/researcher.md",
    ".agents/agents/frontend-architect.md",
    ".agents/agents/staff-backend.md",
    ".agents/agents/database-sre.md",
    ".agents/agents/devsecops-principal.md",
    ".agents/agents/qa-automation-lead.md",
    ".agents/skills/architecture/SKILL.md",
    ".agents/skills/caveman/SKILL.md",
    ".agents/skills/code-quality/SKILL.md",
    ".agents/skills/data-engineering/SKILL.md",
    ".agents/skills/deep-research/SKILL.md",
    ".agents/skills/design/SKILL.md",
    ".agents/skills/devops/SKILL.md",
    ".agents/skills/observability/SKILL.md",
    ".agents/skills/security/SKILL.md",
    ".agents/skills/semantic-graphing/SKILL.md",
    ".agents/skills/verification/SKILL.md",
    "scripts/validate.py",
    "scripts/verify.py",
    "scripts/health_check.py",
    "scripts/grounding.py",
    "scripts/dag_orchestrator.py",
    "scripts/yaml_loader.py",
    "scripts/meeting_coordinator.py",
    "scripts/inbox_manager.py",
    "scripts/intent_guard.py",
    "scripts/neurosymbolic_engine.py",
    "scripts/test_quality_guard.py",
    "scripts/complexity_analyzer.py",
    "scripts/dry_guard.py",
    "scripts/git_hygiene_guard.py",
    "scripts/upgrade.py",
    "scripts/ui_hygiene_guard.py",
    "scripts/self_learner.py",
    "scripts/memory_consolidator.py",
    "scripts/auto_reviewer.py",
    "scripts/autonomous_loop.py",
    "scripts/hermes_manager.py",
    "scripts/intent_compiler.py",
    "scripts/start.py",
    "scripts/hooks/hook_utils.py",
    "scripts/hooks/post_invoke_telemetry.py",
    "scripts/hooks/pre_invoke_master.py",
    "scripts/hooks/pre_tool_quality_gate.py",
)

REQUIRED_PATHS = CORE_AGENT_PATHS + ("scripts/semantic_grapher.py",)
CONSUMER_REQUIRED_PATHS = CORE_AGENT_PATHS

OPTIONAL_PATHS = (
    ".agents/brain/rules.md",
    ".agents/brain/memory.md",
    ".agents/brain/active_context.md",
    ".agents/brain/ANCHOR.md",
    ".agents/brain/schema.md",
    ".agents/brain/env-required.json",
)


def is_framework_repo() -> bool:
    """Check if running directly inside the upstream AAC framework repository."""
    for script_name in ("install.py", "install.sh"):
        candidate = ROOT / script_name
        if candidate.is_file():
            try:
                content = candidate.read_text(encoding="utf-8")
                if "antigravity-agents" in content:
                    return True
            except (OSError, UnicodeDecodeError) as exc:
                sys.stderr.write(f"Notice: Failed to read {script_name}: {exc}\n")
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


def validate_mcp_config_dict(config: dict, file_label: str) -> None:
    servers = config.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        fail(f"{file_label} must define mcpServers")
    for name, server in servers.items():
        if not isinstance(server, dict):
            fail(f"MCP server {name} in {file_label} must be an object")
        if "serverURL" in server:
            fail(f"MCP server {name} in {file_label} uses deprecated serverURL; use serverUrl")
        if "serverUrl" not in server and "command" not in server:
            fail(f"MCP server {name} in {file_label} needs serverUrl or command")
        if server.get("serverUrl") and not str(server["serverUrl"]).startswith("https://"):
            fail(f"remote MCP server {name} in {file_label} must use HTTPS")
        args = server.get("args", [])
        if not isinstance(args, list) or any(not isinstance(item, str) for item in args):
            fail(f"MCP server {name} in {file_label} args must be an array of strings")
        if any(item.endswith(":latest") for item in args):
            fail(f"MCP server {name} in {file_label} uses mutable :latest image")


def validate_server_properties(srv: str, ex_srv: dict, act_srv: dict) -> None:
    if set(ex_srv.keys()) != set(act_srv.keys()):
        fail(f"mcpServers.{srv} property mismatch between example and actual: {set(ex_srv.keys()) ^ set(act_srv.keys())}")
    if "command" in ex_srv:
        if ex_srv["command"] != act_srv.get("command"):
            fail(f"mcpServers.{srv}.command mismatch: {ex_srv['command']} vs {act_srv.get('command')}")
    if "args" in ex_srv:
        if ex_srv["args"] != act_srv.get("args"):
            fail(f"mcpServers.{srv}.args mismatch: {ex_srv['args']} vs {act_srv.get('args')}")
    if "env" in ex_srv:
        if "env" not in act_srv or set(ex_srv["env"].keys()) != set(act_srv["env"].keys()):
            fail(f"mcpServers.{srv}.env key mismatch between example and actual: {set(ex_srv['env'].keys()) ^ set(act_srv.get('env', {}).keys())}")
        if ex_srv["env"] != act_srv["env"]:
            fail(f"mcpServers.{srv}.env value mismatch: {ex_srv['env']} vs {act_srv['env']}")


def validate_mcp() -> None:
    example_config = load_json(".agents/mcp_config.json.example")
    validate_mcp_config_dict(example_config, ".agents/mcp_config.json.example")
    actual_path = ROOT / ".agents" / "mcp_config.json"
    if actual_path.is_file():
        actual_config = load_json(".agents/mcp_config.json")
        validate_mcp_config_dict(actual_config, ".agents/mcp_config.json")
        ex_servers = set(example_config.get("mcpServers", {}).keys())
        act_servers = set(actual_config.get("mcpServers", {}).keys())
        if ex_servers != act_servers:
            fail(f"mcpServers key mismatch between example and actual: {ex_servers ^ act_servers}")
        for srv in ex_servers:
            validate_server_properties(srv, example_config["mcpServers"][srv], actual_config["mcpServers"][srv])



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
    for relative_path, maximum in (("AGENTS.md", 750), ("GEMINI.md", 80), ("agent.md", 80), (".agents/TASK_TEMPLATE.md", 500)):
        target = ROOT / relative_path
        if target.is_file():
            words = target.read_text(encoding="utf-8").split()
            if len(words) > maximum:
                fail(f"{relative_path} exceeds the {maximum}-word always-on budget")
    bootstrap = (ROOT / "GEMINI.md").read_text(encoding="utf-8")
    if "AGENTS.md" not in bootstrap:
        fail("GEMINI.md must bootstrap AGENTS.md")


def validate_single_settings_file(target: str) -> None:
    settings = load_json(target)
    required = {
        "toolPermission": "always-proceed",
        "enableTerminalSandbox": False,
        "allowNonWorkspaceAccess": True,
        "artifactReviewPolicy": "auto",
    }
    for key, expected in required.items():
        if settings.get(key) != expected:
            fail(f"{target} baseline must set {key}={expected!r}")
    permissions = settings.get("permissions")
    if not isinstance(permissions, dict):
        fail(f"{target} baseline must define permissions")
    for key in ("allow", "deny"):
        if not isinstance(permissions.get(key), list) or not permissions[key]:
            fail(f"{target} permissions.{key} must be a non-empty list")
    if not any(item.startswith("command(") for item in permissions["deny"]):
        fail(f"{target} baseline must deny at least one command")
    trusted = settings.get("trustedWorkspaces")
    if not isinstance(trusted, list) or not trusted or not all(isinstance(w, str) and w for w in trusted):
        fail(f"{target} trustedWorkspaces must be a non-empty list of paths")


def validate_settings() -> None:
    example_path = ".agents/antigravity-settings.example.json"
    validate_single_settings_file(example_path)
    actual_path = ROOT / ".agents" / "antigravity-settings.json"
    if actual_path.is_file():
        validate_single_settings_file(".agents/antigravity-settings.json")
        ex_settings = load_json(example_path)
        act_settings = load_json(".agents/antigravity-settings.json")
        if set(ex_settings.keys()) != set(act_settings.keys()):
            fail(f"Settings key mismatch between example and actual: {set(ex_settings.keys()) ^ set(act_settings.keys())}")
        for k in ex_settings:
            if k in ("trustedWorkspaces", "permissions"):
                continue
            if ex_settings[k] != act_settings.get(k):
                fail(f"Settings property '{k}' mismatch between example and actual: {ex_settings[k]} vs {act_settings.get(k)}")
        ex_perms = ex_settings.get("permissions", {})
        act_perms = act_settings.get("permissions", {})
        if set(ex_perms.keys()) != set(act_perms.keys()):
            fail(f"Permissions key mismatch between example and actual: {set(ex_perms.keys()) ^ set(act_perms.keys())}")
        if ex_perms.get("allow", []) != act_perms.get("allow", []):
            fail(f"Permissions allow list mismatch: {ex_perms.get('allow')} vs {act_perms.get('allow')}")
        if ex_perms.get("deny") != act_perms.get("deny"):
            fail(f"Permissions deny list mismatch: {ex_perms.get('deny')} vs {act_perms.get('deny')}")
        if ex_perms.get("ask") != act_perms.get("ask"):
            fail(f"Permissions ask list mismatch: {ex_perms.get('ask')} vs {act_perms.get('ask')}")

    cli_settings_path = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
    if cli_settings_path.is_file():
        validate_single_settings_file(str(cli_settings_path))
        cli_settings = load_json(str(cli_settings_path))
        ex_settings = load_json(example_path)
        if set(ex_settings.keys()) != set(cli_settings.keys()):
            fail(f"Settings key mismatch between example and CLI actual: {set(ex_settings.keys()) ^ set(cli_settings.keys())}")
        for k in ex_settings:
            if k in ("trustedWorkspaces", "permissions"):
                continue
            if ex_settings[k] != cli_settings.get(k):
                fail(f"Settings property '{k}' mismatch between example and CLI actual: {ex_settings[k]} vs {cli_settings.get(k)}")
        ex_perms = ex_settings.get("permissions", {})
        cli_perms = cli_settings.get("permissions", {})
        if set(ex_perms.keys()) != set(cli_perms.keys()):
            fail(f"Permissions key mismatch between example and CLI actual: {set(ex_perms.keys()) ^ set(cli_perms.keys())}")
        if ex_perms.get("allow", []) != cli_perms.get("allow", []):
            fail(f"Permissions allow list mismatch with CLI actual: {ex_perms.get('allow')} vs {cli_perms.get('allow')}")
        if ex_perms.get("deny") != cli_perms.get("deny"):
            fail(f"Permissions deny list mismatch with CLI actual: {ex_perms.get('deny')} vs {cli_perms.get('deny')}")
        if ex_perms.get("ask") != cli_perms.get("ask"):
            fail(f"Permissions ask list mismatch with CLI actual: {ex_perms.get('ask')} vs {cli_perms.get('ask')}")


def validate_env() -> None:
    example_path = ROOT / ".env.example"
    actual_path = ROOT / ".env"
    if not example_path.is_file():
        fail(".env.example must exist")

    def parse_env_keys(p: Path) -> set[str]:
        keys = set()
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                keys.add(line.split("=", 1)[0])
        return keys

    ex_keys = parse_env_keys(example_path)
    if actual_path.is_file():
        act_keys = parse_env_keys(actual_path)
        if ex_keys != act_keys:
            fail(f".env key mismatch between example and actual: {ex_keys ^ act_keys}")


def validate_handoff_template() -> None:
    tpl_path = ROOT / "handoff_template.json"
    if not tpl_path.is_file():
        return
    try:
        from scripts.neurosymbolic_engine import validate_handoff
        if not validate_handoff(tpl_path):
            fail("handoff_template.json failed neurosymbolic validation")
    except ImportError as exc:
        fail(f"Could not import neurosymbolic_engine for handoff validation: {exc}")


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
        validate_markdown_metadata(".agents/agents", 5, ("name", "description", "mode", "model", "tools"))
        validate_markdown_metadata(".agents/rules", 5, ("name", "description", "trigger"), "*.md")
        validate_instruction_budget()
        validate_settings()
        validate_env()
        validate_handoff_template()
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
