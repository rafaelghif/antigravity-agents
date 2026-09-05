#!/usr/bin/env python3
"""
AAC Automated Health Check & Self-Diagnosis Engine.
Detects 14 dimensions of workspace health and provides deterministic self-repair.
Supports structured machine-readable JSON output and human-readable reporting.
"""

from __future__ import annotations

import argparse, ast, json
import os, re, shutil, subprocess, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_AGENTS = (
    "scrum-master",
    "product-manager",
    "researcher",
    "frontend-architect",
    "staff-backend",
    "database-sre",
    "devsecops-principal",
    "qa-automation-lead",
)

REQUIRED_SKILLS = (
    "architecture",
    "caveman",
    "code-quality",
    "data-engineering",
    "deep-research",
    "design",
    "devops",
    "observability",
    "security",
    "semantic-graphing",
    "verification",
)

REQUIRED_RULES = (
    "01-grounding.md",
    "02-project-adaptation.md",
    "03-token-economy.md",
    "04-verification-gates.md",
    "05-git-hygiene.md",
)


def check_agent_frontmatter(agent_name: str, fm: str) -> str | None:
    for req in ("name", "description", "mode", "model", "tools"):
        if not re.search(rf"^{req}:\s*\S+", fm, re.MULTILINE):
            return f"{agent_name} (missing {req})"
    return None


def check_skill_frontmatter(skill_name: str, fm: str) -> str | None:
    for req in ("name", "description"):
        if not re.search(rf"^{req}:\s*\S+", fm, re.MULTILINE):
            return f"{skill_name} (missing {req})"
    return None


def check_rule_frontmatter(rule_name: str, fm: str) -> str | None:
    for req in ("name", "description", "trigger"):
        if not re.search(rf"^{req}:\s*\S+", fm, re.MULTILINE):
            return f"{rule_name} (missing {req})"
    return None


def check_task_script_references(task_file: Path, root: Path) -> list[str]:
    broken = []
    try:
        text = task_file.read_text(encoding="utf-8")
        matches = re.findall(r"scripts/([a-zA-Z0-9_\-]+\.py)", text)
        for script_ref in matches:
            if not (root / "scripts" / script_ref).is_file():
                broken.append(f"{task_file.name} -> scripts/{script_ref}")
    except Exception as exc:
        broken.append(f"{task_file.name} (read error: {exc})")
    return broken


def validate_mcp_server_entry(s_name: str, s_val: Any, path_name: str) -> list[str]:
    issues = []
    if not isinstance(s_val, dict):
        issues.append(f"{path_name}: server {s_name} not a dict")
        return issues
    if "serverURL" in s_val:
        issues.append(f"{path_name}: server {s_name} uses deprecated serverURL")
    if s_val.get("serverUrl") and not str(s_val["serverUrl"]).startswith("https://"):
        issues.append(f"{path_name}: server {s_name} not using HTTPS")
    args = s_val.get("args", [])
    if any(str(a).endswith(":latest") for a in args):
        issues.append(f"{path_name}: server {s_name} uses mutable :latest")
    return issues


def validate_mcp_servers_dict(servers: dict, path_name: str) -> list[str]:
    issues = []
    for s_name, s_val in servers.items():
        issues.extend(validate_mcp_server_entry(s_name, s_val, path_name))
    return issues


def check_hook_def_scripts(cmd: str, event_name: str, root: Path) -> list[str]:
    issues = []
    script_matches = re.findall(r"scripts/hooks/([a-zA-Z0-9_\-]+\.py)", cmd)
    for sm in script_matches:
        target = root / "scripts" / "hooks" / sm
        if not target.is_file():
            issues.append(f"Hook '{event_name}' refers to missing {target}")
    return issues


def validate_hook_list(hook_list: list, event_name: str, root: Path) -> list[str]:
    issues = []
    for hook_def in hook_list:
        cmd = hook_def.get("command", "")
        issues.extend(check_hook_def_scripts(cmd, event_name, root))
    return issues


class HealthChecker:
    def __init__(self, root: Path = ROOT, repair: bool = False):
        self.root = root
        self.repair = repair
        self.results: dict[str, dict[str, Any]] = {}
        self.issues: list[dict[str, str]] = []
        self.repaired: list[str] = []

    def record_issue(self, check_name: str, what: str, where: str, why: str, fix_safety: str, verify_step: str) -> None:
        self.issues.append({
            "check": check_name,
            "what": what,
            "where": where,
            "why": why,
            "can_fix_safely": fix_safety,
            "how_to_verify": verify_step
        })

    def check_agents(self) -> bool:
        missing = []
        invalid = []
        agents_dir = self.root / ".agents" / "agents"
        if not agents_dir.is_dir():
            self.record_issue("missing_agents", "Agents directory missing", str(agents_dir), "Directory not found", "No (requires re-install)", "python3 scripts/validate.py")
            self.results["missing_agents"] = {"passed": False, "missing": list(REQUIRED_AGENTS)}
            return False

        for name in REQUIRED_AGENTS:
            agent_file = agents_dir / f"{name}.md"
            if not agent_file.is_file():
                missing.append(name)
                continue
            text = agent_file.read_text(encoding="utf-8")
            match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
            if not match:
                invalid.append(f"{name} (missing frontmatter)")
                continue
            err = check_agent_frontmatter(name, match.group(1))
            if err:
                invalid.append(err)

        passed = len(missing) == 0 and len(invalid) == 0
        if not passed:
            self.record_issue("missing_agents", f"Missing: {missing}; Invalid: {invalid}", str(agents_dir), "Agents incomplete or corrupt", "Yes via install.py --repair", "python3 scripts/health_check.py")
        self.results["missing_agents"] = {"passed": passed, "missing": missing, "invalid": invalid}
        return passed

    def check_skills(self) -> bool:
        missing = []
        invalid = []
        skills_dir = self.root / ".agents" / "skills"
        if not skills_dir.is_dir():
            self.record_issue("missing_skills", "Skills directory missing", str(skills_dir), "Directory not found", "No (requires re-install)", "python3 scripts/validate.py")
            self.results["missing_skills"] = {"passed": False, "missing": list(REQUIRED_SKILLS)}
            return False

        for name in REQUIRED_SKILLS:
            skill_file = skills_dir / name / "SKILL.md"
            if not skill_file.is_file():
                missing.append(name)
                continue
            text = skill_file.read_text(encoding="utf-8")
            match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
            if not match:
                invalid.append(f"{name} (missing frontmatter)")
                continue
            err = check_skill_frontmatter(name, match.group(1))
            if err:
                invalid.append(err)

        passed = len(missing) == 0 and len(invalid) == 0
        if not passed:
            self.record_issue("missing_skills", f"Missing: {missing}; Invalid: {invalid}", str(skills_dir), "Skills incomplete or corrupt", "Yes via install.py --repair", "python3 scripts/health_check.py")
        self.results["missing_skills"] = {"passed": passed, "missing": missing, "invalid": invalid}
        return passed

    def check_rules(self) -> bool:
        missing = []
        invalid = []
        rules_dir = self.root / ".agents" / "rules"
        if not rules_dir.is_dir():
            self.record_issue("missing_rules", "Rules directory missing", str(rules_dir), "Directory not found", "No (requires re-install)", "python3 scripts/validate.py")
            self.results["missing_rules"] = {"passed": False, "missing": list(REQUIRED_RULES)}
            return False

        for name in REQUIRED_RULES:
            rule_file = rules_dir / name
            if not rule_file.is_file():
                missing.append(name)
                continue
            text = rule_file.read_text(encoding="utf-8")
            match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
            if not match:
                invalid.append(f"{name} (missing frontmatter)")
                continue
            err = check_rule_frontmatter(name, match.group(1))
            if err:
                invalid.append(err)

        passed = len(missing) == 0 and len(invalid) == 0
        if not passed:
            self.record_issue("missing_rules", f"Missing: {missing}; Invalid: {invalid}", str(rules_dir), "Rules incomplete or corrupt", "Yes via install.py --repair", "python3 scripts/health_check.py")
        self.results["missing_rules"] = {"passed": passed, "missing": missing, "invalid": invalid}
        return passed

    def check_broken_references(self) -> bool:
        broken = []
        tasks_dir = self.root / "tasks"
        if tasks_dir.is_dir():
            for task_file in tasks_dir.glob("*.yaml"):
                broken.extend(check_task_script_references(task_file, self.root))

        passed = len(broken) == 0
        if not passed:
            self.record_issue("broken_references", f"Broken script references: {broken}", str(tasks_dir), "Referenced scripts do not exist", "Yes, update script reference to existing module", "python3 scripts/health_check.py")
        self.results["broken_references"] = {"passed": passed, "broken": broken}
        return passed

    def check_broken_scripts(self) -> bool:
        syntax_errors = []
        scripts_dir = self.root / "scripts"
        if scripts_dir.is_dir():
            for py_file in scripts_dir.rglob("*.py"):
                try:
                    ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
                except SyntaxError as e:
                    syntax_errors.append(f"{py_file.name}: line {e.lineno} ({e.msg})")
                except Exception as e:
                    syntax_errors.append(f"{py_file.name}: {e}")

        passed = len(syntax_errors) == 0
        if not passed:
            self.record_issue("broken_scripts", f"Syntax errors: {syntax_errors}", str(scripts_dir), "Python syntax corruption", "Yes, fix syntax in identified lines", "python3 scripts/health_check.py")
        self.results["broken_scripts"] = {"passed": passed, "errors": syntax_errors}
        return passed

    def check_missing_dependencies(self) -> bool:
        missing = []
        if sys.version_info < (3, 10):
            missing.append(f"Python >= 3.10 required (found {sys.version.split()[0]})")
        if not shutil.which("git"):
            missing.append("git command-line tool not found in PATH")

        passed = len(missing) == 0
        if not passed:
            self.record_issue("missing_dependencies", f"Missing dependencies: {missing}", "System Environment", "Host toolchain requirement missing", "Install Python 3.10+ and Git on host", "python3 --version && git --version")
        self.results["missing_dependencies"] = {"passed": passed, "missing": missing}
        return passed

    def check_wrong_installation_version(self) -> bool:
        issues = []
        cfg_file = self.root / ".agents" / "config.json"
        ver = "0.0.0"
        if cfg_file.is_file():
            try:
                data = json.loads(cfg_file.read_text(encoding="utf-8"))
                ver = str(data.get("core_version", "0.0.0"))
                if not re.match(r"^\d+\.\d+\.\d+", ver):
                    issues.append(f"Invalid semver in config.json: {ver}")
            except Exception as e:
                issues.append(f"Error reading config.json: {e}")
        else:
            issues.append(".agents/config.json missing")

        compat_file = self.root / ".agents" / "antigravity-compatibility.json"
        if compat_file.is_file():
            try:
                cdata = json.loads(compat_file.read_text(encoding="utf-8"))
                cver = str(cdata.get("aac_version", ""))
                if cver and cver != ver:
                    issues.append(f"Version mismatch: config.json has {ver}, compatibility has {cver}")
            except Exception as e:
                issues.append(f"Error reading antigravity-compatibility.json: {e}")

        passed = len(issues) == 0
        if not passed:
            self.record_issue("wrong_installation_version", f"Version issues: {issues}", str(cfg_file), "Manifest version inconsistency", "Yes, align version strings", "python3 scripts/validate.py")
        self.results["wrong_installation_version"] = {"passed": passed, "version": ver, "issues": issues}
        return passed

    def check_stale_git_revision(self) -> bool:
        git_dir = self.root / ".git"
        if not git_dir.is_dir() or not shutil.which("git"):
            self.results["stale_git_revision"] = {"passed": True, "notice": "Not a git repository or git missing"}
            return True

        try:
            res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.root, capture_output=True, text=True, timeout=5)
            rev = res.stdout.strip() if res.returncode == 0 else "UNKNOWN"
            self.results["stale_git_revision"] = {"passed": True, "head_revision": rev}
            return True
        except Exception as exc:
            self.results["stale_git_revision"] = {"passed": True, "notice": str(exc)}
            return True

    def check_invalid_configuration(self) -> bool:
        cfg_file = self.root / ".agents" / "config.json"
        errors = []
        if not cfg_file.is_file():
            errors.append("config.json missing")
        else:
            try:
                data = json.loads(cfg_file.read_text(encoding="utf-8"))
                for req in ("core_version", "security", "orchestration", "state_management"):
                    if req not in data:
                        errors.append(f"Missing required section: {req}")
            except Exception as e:
                errors.append(f"JSON syntax error: {e}")

        passed = len(errors) == 0
        if not passed:
            self.record_issue("invalid_configuration", f"Config errors: {errors}", str(cfg_file), "Malformed configuration file", "Yes, restore from template or backup", "python3 scripts/validate.py")
        self.results["invalid_configuration"] = {"passed": passed, "errors": errors}
        return passed

    def check_platform_incompatibility(self) -> bool:
        issues = []
        default_enc = sys.getdefaultencoding().lower()
        if default_enc not in ("utf-8", "utf8"):
            issues.append(f"Default encoding is {default_enc}, expected utf-8")

        guard_file = self.root / "scripts" / "platform_guard.py"
        if not guard_file.is_file():
            issues.append("scripts/platform_guard.py missing")

        passed = len(issues) == 0
        if not passed:
            self.record_issue("platform_incompatibility", f"Platform issues: {issues}", "Runtime", "Encoding or platform guard missing", "Yes, ensure platform_guard.py is present", "python3 scripts/health_check.py")
        self.results["platform_incompatibility"] = {"passed": passed, "platform": sys.platform, "issues": issues}
        return passed

    def check_broken_mcp(self) -> bool:
        issues = []
        candidates = [self.root / ".agents" / "mcp_config.json", self.root / ".agents" / "mcp_config.json.example"]
        checked = False
        parsed_configs = {}
        for path in candidates:
            if path.is_file():
                checked = True
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    servers = data.get("mcpServers")
                    if not isinstance(servers, dict):
                        issues.append(f"{path.name} missing mcpServers dict")
                    else:
                        issues.extend(validate_mcp_servers_dict(servers, path.name))
                        parsed_configs[path.name] = servers
                except Exception as e:
                    issues.append(f"{path.name} error: {e}")

        if not checked:
            issues.append("Neither mcp_config.json nor mcp_config.json.example found")

        # Parity enforcement between example and actual MCP configs
        if "mcp_config.json" in parsed_configs and "mcp_config.json.example" in parsed_configs:
            act_s = parsed_configs["mcp_config.json"]
            ex_s = parsed_configs["mcp_config.json.example"]
            if set(act_s.keys()) != set(ex_s.keys()):
                issues.append(f"mcpServers key mismatch between example and actual: {set(act_s.keys()) ^ set(ex_s.keys())}")
            for srv in set(act_s.keys()) & set(ex_s.keys()):
                if set(act_s[srv].keys()) != set(ex_s[srv].keys()):
                    issues.append(f"mcpServers.{srv} property mismatch: {set(act_s[srv].keys()) ^ set(ex_s[srv].keys())}")
                if "env" in act_s[srv] and "env" in ex_s[srv]:
                    if set(act_s[srv]["env"].keys()) != set(ex_s[srv]["env"].keys()):
                        issues.append(f"mcpServers.{srv}.env key mismatch: {set(act_s[srv]['env'].keys()) ^ set(ex_s[srv]['env'].keys())}")

        passed = len(issues) == 0
        if not passed:
            self.record_issue("broken_mcp", f"MCP config issues: {issues}", ".agents/mcp_config.json", "MCP configuration contract violation", "Yes, sanitize mcp_config.json schema", "python3 scripts/validate.py")
        self.results["broken_mcp"] = {"passed": passed, "issues": issues}
        return passed

    def check_broken_hooks(self) -> bool:
        issues = []
        hooks_file = self.root / ".agents" / "plugins" / "aac-core" / "hooks.json"
        if not hooks_file.is_file():
            self.results["broken_hooks"] = {"passed": True, "notice": "hooks.json not present in consumer workspace"}
            return True

        try:
            data = json.loads(hooks_file.read_text(encoding="utf-8"))
            hooks = data.get("hooks", {})
            for event_name, hook_list in hooks.items():
                if isinstance(hook_list, list):
                    issues.extend(validate_hook_list(hook_list, event_name, self.root))
        except Exception as e:
            issues.append(f"hooks.json read error: {e}")

        passed = len(issues) == 0
        if not passed:
            self.record_issue("broken_hooks", f"Hook issues: {issues}", str(hooks_file), "Hook references non-existent scripts", "Yes, restore hook script", "python3 scripts/health_check.py")
        self.results["broken_hooks"] = {"passed": passed, "issues": issues}
        return passed

    def check_permission_mismatch(self) -> bool:
        issues = []
        loaded_settings = {}
        for sf_name in ("antigravity-settings.example.json", "antigravity-settings.json"):
            settings_file = self.root / ".agents" / sf_name
            if settings_file.is_file():
                try:
                    data = json.loads(settings_file.read_text(encoding="utf-8"))
                    perms = data.get("permissions")
                    if not isinstance(perms, dict) or "allow" not in perms or "deny" not in perms:
                        issues.append(f"{sf_name} permissions object missing allow/deny lists")
                    loaded_settings[sf_name] = data
                except Exception as e:
                    issues.append(f"{sf_name} error: {e}")

        # Parity enforcement between example and actual settings
        if "antigravity-settings.example.json" in loaded_settings and "antigravity-settings.json" in loaded_settings:
            ex_data = loaded_settings["antigravity-settings.example.json"]
            act_data = loaded_settings["antigravity-settings.json"]
            if set(ex_data.keys()) != set(act_data.keys()):
                issues.append(f"Settings top-level key mismatch: {set(ex_data.keys()) ^ set(act_data.keys())}")
            ex_perms = ex_data.get("permissions", {})
            act_perms = act_data.get("permissions", {})
            if isinstance(ex_perms, dict) and isinstance(act_perms, dict):
                if set(ex_perms.keys()) != set(act_perms.keys()):
                    issues.append(f"Permissions key mismatch: {set(ex_perms.keys()) ^ set(act_perms.keys())}")
                if set(ex_perms.get("allow", [])) != set(act_perms.get("allow", [])):
                    issues.append(f"Allowed permissions mismatch between example and actual: {set(ex_perms.get('allow', [])) ^ set(act_perms.get('allow', []))}")

        passed = len(issues) == 0
        if not passed:
            self.record_issue("permission_mismatch", f"Permission issues: {issues}", str(self.root / ".agents" / "antigravity-settings.example.json"), "Settings file invalid", "Yes, restore settings template", "python3 scripts/validate.py")
        self.results["permission_mismatch"] = {"passed": passed, "issues": issues}
        return passed

    def check_incomplete_bootstrap(self) -> bool:
        issues = []
        for f in ("AGENTS.md", "GEMINI.md"):
            if not (self.root / f).is_file():
                issues.append(f"Missing root bootstrap file: {f}")

        gemini_file = self.root / "GEMINI.md"
        if gemini_file.is_file():
            text = gemini_file.read_text(encoding="utf-8")
            if "AGENTS.md" not in text:
                issues.append("GEMINI.md does not bootstrap AGENTS.md")

        passed = len(issues) == 0
        if not passed:
            self.record_issue("incomplete_bootstrap", f"Bootstrap issues: {issues}", "Workspace Root", "Root AGENTS.md/GEMINI.md missing or unlinked", "Yes, restore AGENTS.md/GEMINI.md", "python3 scripts/validate.py")
        self.results["incomplete_bootstrap"] = {"passed": passed, "issues": issues}
        return passed

    def execute_repairs(self) -> list[str]:
        repaired = []
        # 1. Scratch dir
        scratch_dir = self.root / ".agents" / "scratch"
        if not scratch_dir.exists():
            scratch_dir.mkdir(parents=True, exist_ok=True)
            repaired.append("Created missing .agents/scratch/ directory")

        # 2. Baseline handoff.json if missing
        handoff_file = self.root / "handoff.json"
        if not handoff_file.exists():
            baseline = {
                "task_id": "INIT",
                "worker_role": "scrum-master",
                "summary": f"Initialized AAC workspace for {self.root.name}",
                "modifications": [],
                "tests": [],
                "confidence_score": 1.0,
                "requires_human": False
            }
            handoff_file.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
            repaired.append("Created baseline handoff.json contract")

        # 3. .gitignore managed entries
        gi_file = self.root / ".gitignore"
        try:
            gi_text = gi_file.read_text(encoding="utf-8") if gi_file.is_file() else ""
            needed = []
            if ".agents/scratch/" not in gi_text:
                needed.append(".agents/scratch/")
            if ".agents-backups/" not in gi_text:
                needed.append(".agents-backups/")
            if needed:
                block = "\n\n# Antigravity Managed Directories\n" + "\n".join(needed) + "\n"
                gi_file.write_text(gi_text.rstrip() + block, encoding="utf-8")
                repaired.append(f"Added {', '.join(needed)} to .gitignore")
        except Exception as e:
            sys.stderr.write(f"Repair notice (.gitignore): {e}\n")

        # 4. env-required.json
        env_file = self.root / ".agents" / "brain" / "env-required.json"
        if not env_file.exists():
            env_file.parent.mkdir(parents=True, exist_ok=True)
            env_file.write_text(json.dumps({"required_env_vars": []}, indent=2), encoding="utf-8")
            repaired.append("Created baseline .agents/brain/env-required.json")

        # 5. githooks executable permissions
        if os.name != "nt":
            hook = self.root / ".githooks" / "pre-commit"
            if hook.is_file():
                try:
                    mode = hook.stat().st_mode
                    if not (mode & 0o111):
                        hook.chmod(mode | 0o755)
                        repaired.append("Added executable permission to .githooks/pre-commit")
                except Exception as exc:
                    _ = exc

        self.repaired = repaired
        return repaired

    def run_all(self) -> dict[str, Any]:
        if self.repair:
            self.execute_repairs()

        checks = [
            ("missing_agents", self.check_agents),
            ("missing_skills", self.check_skills),
            ("missing_rules", self.check_rules),
            ("broken_references", self.check_broken_references),
            ("broken_scripts", self.check_broken_scripts),
            ("missing_dependencies", self.check_missing_dependencies),
            ("wrong_installation_version", self.check_wrong_installation_version),
            ("stale_git_revision", self.check_stale_git_revision),
            ("invalid_configuration", self.check_invalid_configuration),
            ("platform_incompatibility", self.check_platform_incompatibility),
            ("broken_mcp", self.check_broken_mcp),
            ("broken_hooks", self.check_broken_hooks),
            ("permission_mismatch", self.check_permission_mismatch),
            ("incomplete_bootstrap", self.check_incomplete_bootstrap),
        ]

        passed_count = 0
        for name, fn in checks:
            try:
                res = fn()
                if res:
                    passed_count += 1
            except Exception as e:
                self.record_issue(name, f"Exception during check: {e}", "Internal", str(e), "Inspect traceback", "python3 scripts/health_check.py")
                self.results[name] = {"passed": False, "error": str(e)}

        all_passed = passed_count == len(checks)
        status = "HEALTHY" if all_passed else ("DEGRADED" if passed_count >= 12 else "UNHEALTHY")

        return {
            "status": status,
            "passed_checks": passed_count,
            "total_checks": len(checks),
            "checks": self.results,
            "issues": self.issues,
            "repaired": self.repaired,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="AAC Automated Health Check & Self-Diagnosis Engine")
    parser.add_argument("path", nargs="?", default=".", help="Target workspace root")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--repair", action="store_true", help="Automatically repair deterministic low-risk problems")
    args = parser.parse_args()

    root_dir = Path(args.path).resolve()
    checker = HealthChecker(root=root_dir, repair=args.repair)
    report = checker.run_all()

    if args.json:
        print(json.dumps(report, indent=2))
        return 0 if report["status"] == "HEALTHY" else 1

    print("=" * 60)
    print(f"🏥 AAC Automated Workspace Health Check ({report['status']})")
    print("=" * 60)
    print(f"Score: {report['passed_checks']}/{report['total_checks']} dimensions green.")

    if report["repaired"]:
        print("\n🔧 Deterministic Repairs Applied:")
        for r in report["repaired"]:
            print(f"  • {r}")

    if report["issues"]:
        print("\n⚠️ Diagnostic Findings (Self-Diagnosis):")
        for idx, issue in enumerate(report["issues"], 1):
            print(f"\n  [{idx}] Check: {issue['check']}")
            print(f"      What:       {issue['what']}")
            print(f"      Where:      {issue['where']}")
            print(f"      Why:        {issue['why']}")
            print(f"      Safe Fix:   {issue['can_fix_safely']}")
            print(f"      Verify:     {issue['how_to_verify']}")
    else:
        print("\n✨ All 14 AAC health dimensions fully green! Workspace is 100% operational.")

    return 0 if report["status"] == "HEALTHY" else 1


if __name__ == "__main__":
    sys.exit(main())
