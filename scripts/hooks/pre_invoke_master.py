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
        "typescript", "python", "javascript", "dry", "solid", "optimization", "clean"
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
    
    # 1. Cross-Session Project Memory
    memory_path = Path('.agents/brain/memory.md')
    if memory_path.exists():
        text = memory_path.read_text(encoding='utf-8').strip()
        if text:
            msgs.append(f"=== PERMANENT CROSS-SESSION PROJECT MEMORY ===\n{text}")
            
    # 2. Long-Term DAG Anchor
    anchor_path = Path('.agents/brain/ANCHOR.md')
    if anchor_path.exists():
        text = anchor_path.read_text(encoding='utf-8').strip()
        if text and text != "(No context yet)":
            msgs.append(f"=== LONG-TERM DAG ANCHOR ===\n{text}")
            
    # 3. Self-Learned Rules & DNA
    rules_path = Path('.agents/brain/rules.md')
    if rules_path.exists():
        text = rules_path.read_text(encoding='utf-8').strip()
        if text:
            msgs.append(f"=== SELF-LEARNED RULES ===\n{text}")
            
    # 4. Dynamic Skill Injection (Eliminates Skill Amnesia)
    skills_to_inject = set()
    if transcript_path and Path(transcript_path).exists():
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            # Check for subagent YAML frontmatter in initial steps
            for line in lines[:3]:
                data = json.loads(line)
                content = str(data.get('content', ''))
                yaml_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
                if yaml_match:
                    skills_to_inject.update(parse_skills_from_frontmatter(yaml_match.group(1)))
            # Scan last user message for task-relevant skill keywords
            recent_text = " ".join(
                str(json.loads(line).get('content', ''))
                for line in lines[-5:]
                if 'USER_INPUT' in str(json.loads(line).get('type', ''))
            )
            if recent_text:
                skills_to_inject.update(detect_skills_from_text(recent_text))
        except Exception as e:
            sys.stderr.write(f"Context extraction notice: {str(e)}\n")

    # Inject detected skills
    for skill in sorted(skills_to_inject):
        skill_path = Path(f'.agents/skills/{skill}/SKILL.md')
        if skill_path.exists():
            msgs.append(f"=== AUTO-INJECTED SKILL: {skill} ===\n{skill_path.read_text(encoding='utf-8').strip()}")

    return "\n\n".join(msgs)

def check_rsi(transcript_path: str | None = None) -> bool:
    if not transcript_path or not Path(transcript_path).exists():
        return False
        
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if not lines:
                return False
            last_line = lines[-1]
            data = json.loads(last_line)
            
            if data.get('type') == 'TOOL_RESPONSE':
                content = str(data.get('content', '')).lower()
                if re.search(r'failed with exit code|error:|exception:|traceback|exit status', content):
                    return True
    except Exception as e:
        sys.stderr.write(f"RSI check notice: {str(e)}\n")
    return False

def main() -> None:
    try:
        input_data = sys.stdin.read()
        if not input_data:
            print("{}")
            return
            
        payload = json.loads(input_data)
        transcript_path = payload.get('transcriptPath')
        
        inject_steps = []
        
        # 1. Context Auto-Injection (Memory + Skills + Anchor)
        context_str = get_context(transcript_path)
        if context_str:
            inject_steps.append({
                "ephemeralMessage": f"SYSTEM MEMORY & SKILL INJECTION (Directly loaded into context to prevent amnesia and ensure L9 execution):\n\n{context_str}"
            })
            
        # 2. RSI Self-Healing
        if check_rsi(transcript_path):
            inject_steps.append({
                "ephemeralMessage": "🚨 RSI PROTOCOL TRIGGERED 🚨: The previous command failed! DO NOT guess the solution. You MUST immediately call `invoke_subagent` to spawn a `reviewer` subagent to analyze the root cause and provide a patch."
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
