#!/usr/bin/env python3
import sys
import json
import re
from pathlib import Path

try:
    from hook_utils import read_safe_stdin
except ImportError:
    from scripts.hooks.hook_utils import read_safe_stdin

SKILL_KEYWORDS = {
    "design": [
        "ui", "ux", "component", "page", "styling", "css", "tailwind", "html",
        "frontend", "view", "button", "modal", "layout", "responsive", "screen",
        "webperf", "performance", "perf", "core web vitals", "lcp", "inp", "cls",
        "lazy loading", "bundle size", "tree-shaking", "speed up", "a11y", "accessibility"
    ],
    "code-quality": [
        "code", "refactor", "function", "class", "method", "bug", "fix", "feature",
        "typescript", "python", "javascript", "solid", "optimization", "clean",
        "dry", "duplicate", "duplication", "deduplicate", "copy-paste", "clone", "redundant", "dedup",
        "simplify", "simplification", "clean code", "over-engineered", "refactor simple",
        "code-simplify", "flatten"
    ],
    "security": [
        "auth", "login", "jwt", "token", "password", "secret", "permission", "rbac",
        "security", "sanitize", "encryption", "hash", "session", "oauth"
    ],
    "architecture": [
        "database", "db", "schema", "table", "model", "orm", "prisma",
        "drizzle", "api", "endpoint", "controller", "service", "repository", "system",
        "idempotency", "idempotent", "retry", "backoff", "jitter", "circuit breaker",
        "outbox", "saga", "distributed", "deadlock", "concurrency", "race condition",
        "api contract", "breaking change", "backward compatibility", "rfc 7807",
        "problem details", "zod validation", "pydantic validation", "dto"
    ],
    "verification": [
        "test", "tests", "testing", "pytest", "jest", "unit", "e2e", "assert",
        "coverage", "spec", "mock", "integration"
    ],
    "caveman": [
        "caveman", "cavemen", "hemat token", "token saving", "terse", "singkat", "compress tokens"
    ],
    "data-engineering": [
        "etl", "elt", "pipeline", "data engineering", "batch processing", "cdc", "debezium",
        "kafka", "backfill", "partitioning", "zero downtime", "expand contract",
        "concurrent index", "lock timeout", "non-blocking migration", "schema evolution"
    ],
    "devops": [
        "docker", "dockerfile", "container", "kubernetes", "k8s", "ci/cd", "terraform",
        "iac", "helm", "deployment", "sre", "mcp", "model context protocol", "mcp server", "mcp setup", "mcp config"
    ],
    "observability": [
        "logging", "metrics", "tracing", "opentelemetry", "otel", "telemetry", "monitor", "alerting", "grafana", "prometheus"
    ],
    "semantic-graphing": [
        "semantic graph", "knowledge graph", "blast radius", "call graph", "dependency tree", "ast scan", "pagerank"
    ],
    "deep-research": [
        "research", "search web", "browse", "documentation", "docs", "lookup", "rfc",
        "investigate", "latest version", "official guide", "api reference"
    ]
}

def parse_skills_from_frontmatter(frontmatter_str: str) -> list[str]:
    inline_match = re.search(r'skills:\s*\[(.*?)\]', frontmatter_str)
    if inline_match:
        return [s.strip().strip("'\"") for s in inline_match.group(1).split(',') if s.strip()]
    multiline_match = re.search(r'(?:^|\n)skills:\s*\n((?:\s*-\s*[^\n]+\n?)+)', frontmatter_str)
    if multiline_match:
        return [m.strip() for m in re.findall(r'^\s*-\s*([a-zA-Z0-9_-]+)', multiline_match.group(1), re.MULTILINE) if m.strip()]
    return []

def detect_skills_from_text(text: str) -> list[str]:
    if not text:
        return ["code-quality"]
    lower_text = text.lower()
    matched = []
    for skill, keywords in SKILL_KEYWORDS.items():
        if any(re.search(r'\b' + re.escape(kw) + r'\b', lower_text) for kw in keywords):
            matched.append(skill)
    if "code-quality" not in matched:
        matched.append("code-quality")
    return matched

ROOT = Path(__file__).resolve().parents[2]

def get_context(transcript_path: str | None = None) -> str:
    msgs = []
    
    # 0. Active Session Context & Working Memory (P0 bootstrap)
    active_path = ROOT / '.agents' / 'brain' / 'active_context.md'
    if active_path.exists():
        raw_active = active_path.read_text(encoding='utf-8').splitlines()
        active_lines = [l for l in raw_active if not l.startswith('> ') and not l.startswith('# ⚡') and l.strip()]
        if active_lines:
            msgs.append("=== ACTIVE SESSION WORKING CONTEXT ===\n" + "\n".join(active_lines))

    # 0.5. Codebase Epistemic Grounding (Prevent Hallucinations)
    try:
        sys.path.insert(0, str(ROOT))
        from scripts.grounding import ground_workspace
        grounding_data = ground_workspace(ROOT)
        eco = list(grounding_data.get("ecosystems", {}).keys())
        eco_str = ", ".join(eco) if eco else "Generic / Multi-language"
        ground_lines = [f"Ecosystem: [{eco_str}]"]
        env = grounding_data.get("environment", {})
        if env and env.get("platform"):
            ground_lines.append(f"OS/Arch: {env.get('platform')} ({env.get('architecture', env.get('machine', 'unknown'))})")
        pkg_mgrs = []
        pms_data = grounding_data.get("package_managers", {})
        if isinstance(pms_data, dict):
            lock_pms = pms_data.get("lockfile_managed", [])
            if lock_pms:
                pkg_mgrs.append(f"Lockfile: {', '.join(lock_pms)}")
            avail_cli = pms_data.get("available_cli", [])
            if avail_cli:
                pkg_mgrs.append(f"CLI: {', '.join(avail_cli[:8])}")
        if pkg_mgrs:
            ground_lines.append("Tooling: " + " | ".join(pkg_mgrs))
        frameworks = grounding_data.get("frameworks", [])
        if frameworks:
            fw_names = [f["name"] if isinstance(f, dict) else str(f) for f in frameworks]
            ground_lines.append("Frameworks: " + ", ".join(fw_names))
        test_runners = grounding_data.get("testing", []) or grounding_data.get("testing_strategies", [])
        if test_runners:
            ground_lines.append("Test Runners: " + ", ".join(test_runners))
        deps = []
        for e, dl in grounding_data.get("dependencies", {}).items():
            if dl:
                deps.append(f"{e}: {', '.join(dl[:10])}")
        if deps:
            ground_lines.append("Confirmed Dependencies: " + " | ".join(deps))
        msgs.append("=== CODEBASE GROUNDING BASELINE ===\n" + "\n".join(ground_lines))
    except Exception as exc:
        sys.stderr.write(f"Grounding hook notice: {exc}\n")

    # 1. Cross-Session Project Memory (only populated lines to conserve tokens)
    memory_path = ROOT / '.agents' / 'brain' / 'memory.md'
    if memory_path.exists():
        raw_lines = memory_path.read_text(encoding='utf-8').splitlines()
        populated = [
            l for l in raw_lines
            if l.strip().startswith('- ')
            and not l.endswith('Auto-detected by agent')
        ]
        if populated:
            msgs.append("=== CROSS-SESSION MEMORY ===\n" + "\n".join(populated[:6]))
            
    # 2. Long-Term DAG Anchor (only if active)
    anchor_path = ROOT / '.agents' / 'brain' / 'ANCHOR.md'
    if anchor_path.exists():
        text = anchor_path.read_text(encoding='utf-8').strip()
        if text and "(No context yet)" not in text and "- Phase: NONE" not in text:
            msgs.append(f"=== DAG ANCHOR ===\n{text}")
            
    # 3. Self-Learned Rules (only active bullet rules, omit header to save tokens)
    rules_path = ROOT / '.agents' / 'brain' / 'rules.md'
    if rules_path.exists():
        raw_rules = rules_path.read_text(encoding='utf-8').splitlines()
        CORE_INVARIANT_TAGS = {
            "[NO_TRASH]", "[USER_PROJECT_FIRST]", "[REALITY_OVER_MEMORY]",
            "[EXISTING_CODE_FIRST]", "[SMALL_CONTEXT_DISCOVERY]",
            "[CROSS_PLATFORM_PORTABILITY]", "[LEAST_PRIVILEGE_EXECUTION]",
            "[CAVEMAN_TOKEN_ECONOMY]"
        }
        active_rules = [
            l for l in raw_rules
            if l.startswith('- ')
            and not l.startswith('- Mutate')
            and not l.startswith('- Prune')
            and not l.startswith('- Evolve')
            and 'NO_SUBAGENT_SANDBOX' not in l
            and 'ZERO SANDBOX' not in l
            and not any(tag in l for tag in CORE_INVARIANT_TAGS)
        ]
        if active_rules:
            msgs.append("=== PROCEDURAL RULES ===\n" + "\n".join(active_rules[:12]))
            
    # 4. Compact Skill Directives (Eliminates token bloat by avoiding full markdown dump)
    skills_to_inject = set()
    recent_text = ""
    if transcript_path and Path(transcript_path).exists():
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for line in lines[:3]:
                try:
                    data = json.loads(line)
                    content = str(data.get('content', ''))
                    yaml_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
                    if yaml_match:
                        skills_to_inject.update(parse_skills_from_frontmatter(yaml_match.group(1)))
                except Exception:
                    continue
            recent_inputs = []
            for line in lines[-5:]:
                try:
                    data = json.loads(line)
                    if 'USER_INPUT' in str(data.get('type', '')):
                        recent_inputs.append(str(data.get('content', '')))
                except Exception:
                    continue
            recent_text = " ".join(recent_inputs)
            if recent_text:
                skills_to_inject.update(detect_skills_from_text(recent_text))
        except Exception as e:
            sys.stderr.write(f"Context extraction notice: {str(e)}\n")

    valid_skill_names = set(SKILL_KEYWORDS.keys())
    skills_dir = ROOT / ".agents" / "skills"
    if skills_dir.is_dir():
        valid_skill_names.update(d.name for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith("."))
    skills_to_inject = {s for s in skills_to_inject if s in valid_skill_names}

    if skills_to_inject:
        skill_list = ", ".join(sorted(skills_to_inject))
        msgs.append(f"=== ACTIVE SKILLS: [{skill_list}] ===\n(Use view_file on relevant .agents/skills/<skill>/SKILL.md if implementing related tasks)")

    # 5. Upgrade Intent Mandate
    if recent_text and any(term in recent_text.lower() for term in ["upgrade", "update agent", "/upgrade", "versi baru", "update framework"]):
        msgs.append("=== UPGRADE MANDATE ===\nUser requested AAC upgrade. Execute 'python3 scripts/upgrade.py' via run_command.")

    return "\n\n".join(msgs)

def main() -> None:
    try:
        input_data = read_safe_stdin()
        if not input_data:
            print("{}")
            return
            
        payload = json.loads(input_data)
        transcript_path = payload.get('transcriptPath')
        
        inject_steps = []
        context_str = get_context(transcript_path)
        if context_str:
            inject_steps.append({
                "ephemeralMessage": f"SYSTEM MEMORY & DIRECTIVES (Compact token footprint):\n\n{context_str}"
            })
            
        if inject_steps:
            print(json.dumps({"injectSteps": inject_steps}))
        else:
            print("{}")
            
    except Exception as e:
        sys.stderr.write(f"Pre-invoke hook notice: {str(e)}\n")
        print("{}")

if __name__ == '__main__':
    main()
