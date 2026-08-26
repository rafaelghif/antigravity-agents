#!/usr/bin/env python3
import sys
import json
import re
from pathlib import Path

SKILL_KEYWORDS = {
    "design": [
        "ui", "ux", "component", "page", "styling", "css", "tailwind", "html",
        "frontend", "view", "button", "modal", "layout", "responsive", "screen"
    ],
    "code-quality": [
        "code", "refactor", "function", "class", "method", "bug", "fix", "feature",
        "typescript", "python", "javascript", "solid", "optimization", "clean"
    ],
    "dry": [
        "dry", "duplicate", "duplication", "deduplicate", "copy-paste", "clone", "redundant", "dedup"
    ],
    "security": [
        "auth", "login", "jwt", "token", "password", "secret", "permission", "rbac",
        "security", "sanitize", "encryption", "hash", "session", "oauth"
    ],
    "architecture": [
        "database", "db", "schema", "migration", "table", "model", "orm", "prisma",
        "drizzle", "api", "endpoint", "controller", "service", "repository", "system"
    ],
    "verification": [
        "test", "tests", "testing", "pytest", "jest", "unit", "e2e", "assert",
        "coverage", "spec", "mock", "integration"
    ],
    "caveman": [
        "caveman", "cavemen", "hemat token", "token saving", "terse", "singkat", "compress tokens"
    ],
    "performance-optimization": [
        "webperf", "performance", "perf", "core web vitals", "lcp", "inp", "cls",
        "lazy loading", "bundle size", "tree-shaking", "speed up"
    ],
    "code-simplification": [
        "simplify", "simplification", "clean code", "over-engineered", "refactor simple",
        "code-simplify", "flatten"
    ]
}

def parse_skills_from_frontmatter(frontmatter_str: str) -> list:
    inline_match = re.search(r'skills:\s*\[(.*?)\]', frontmatter_str)
    if inline_match:
        return [s.strip().strip("'\"") for s in inline_match.group(1).split(',') if s.strip()]
    list_match = re.findall(r'^\s*-\s*([a-zA-Z0-9_-]+)', frontmatter_str, re.MULTILINE)
    return list_match

def detect_skills_from_text(text: str) -> list:
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

def get_context(transcript_path: str | None = None) -> str:
    msgs = []
    
    # 1. Cross-Session Project Memory (only populated lines to conserve tokens)
    memory_path = Path('.agents/brain/memory.md')
    if memory_path.exists():
        raw_lines = memory_path.read_text(encoding='utf-8').splitlines()
        populated = [l for l in raw_lines if not l.endswith('Auto-detected by agent') and l.strip()]
        if populated:
            msgs.append("=== CROSS-SESSION MEMORY ===\n" + "\n".join(populated))
            
    # 2. Long-Term DAG Anchor (only if active)
    anchor_path = Path('.agents/brain/ANCHOR.md')
    if anchor_path.exists():
        text = anchor_path.read_text(encoding='utf-8').strip()
        if text and text != "(No context yet)":
            msgs.append(f"=== DAG ANCHOR ===\n{text}")
            
    # 3. Self-Learned Rules (only active bullet rules, omit header to save tokens)
    rules_path = Path('.agents/brain/rules.md')
    if rules_path.exists():
        raw_rules = rules_path.read_text(encoding='utf-8').splitlines()
        active_rules = [l for l in raw_rules if l.startswith('- ')]
        if active_rules:
            msgs.append("=== PROCEDURAL RULES ===\n" + "\n".join(active_rules))
            
    # 4. Compact Skill Directives (Eliminates token bloat by avoiding full markdown dump)
    skills_to_inject = set()
    recent_text = ""
    if transcript_path and Path(transcript_path).exists():
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for line in lines[:3]:
                data = json.loads(line)
                content = str(data.get('content', ''))
                yaml_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
                if yaml_match:
                    skills_to_inject.update(parse_skills_from_frontmatter(yaml_match.group(1)))
            recent_text = " ".join(
                str(json.loads(line).get('content', ''))
                for line in lines[-5:]
                if 'USER_INPUT' in str(json.loads(line).get('type', ''))
            )
            if recent_text:
                skills_to_inject.update(detect_skills_from_text(recent_text))
        except Exception as e:
            sys.stderr.write(f"Context extraction notice: {str(e)}\n")

    if skills_to_inject:
        skill_list = ", ".join(sorted(skills_to_inject))
        msgs.append(f"=== ACTIVE SKILLS: [{skill_list}] ===\n(Use view_file on relevant .agents/skills/<skill>/SKILL.md if implementing related tasks)")

    # 5. Upgrade Intent Mandate
    if recent_text and any(term in recent_text.lower() for term in ["upgrade", "update agent", "/upgrade", "versi baru", "update framework"]):
        msgs.append("=== UPGRADE MANDATE ===\nUser requested AAC upgrade. Execute 'python3 scripts/upgrade.py' via run_command.")

    return "\n\n".join(msgs)

def main() -> None:
    try:
        input_data = sys.stdin.read()
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
