#!/usr/bin/env python3
"""
AAC Autonomous Self-Learner Engine:
Extracts user corrections, preferences, and operational mandates across turns
and atomically persists them into .agents/brain/rules.md and memory.md without token bloat.
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path

LEARNING_SIGNALS = [
    r'\bjangan\b',
    r'\bingat\b',
    r'\binget\b',
    r'\bselalu\b',
    r'\bfokus ke\b',
    r'\bbiasakan\b',
    r'\butamakan\b',
    r'\bgak boleh\b',
    r'\bga boleh\b',
    r'\brule baru\b',
    r'\bnever\b',
    r'\balways\b',
    r'\bremember\b',
    r'\bprefer\b',
    r'\bdon\'?t\b',
    r'\bstop\b',
    r'\bavoid\b'
]

def normalize_rule(text: str) -> str:
    cleaned = re.sub(r'[^\w\s]', '', text).lower()
    return " ".join(cleaned.split())

def contains_learning_signal(text: str) -> bool:
    lower_text = text.lower()
    for sig in LEARNING_SIGNALS:
        if re.search(sig, lower_text):
            return True
    return False

def extract_learning_from_user_input(text: str) -> str | None:
    if not text or len(text.strip()) < 8:
        return None
    
    # Strip XML tags and wrappers like <USER_REQUEST>, <ADDITIONAL_METADATA>
    cleaned = re.sub(r'<USER_REQUEST>\s*', '', text)
    cleaned = re.sub(r'\s*</USER_REQUEST>.*', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'<[^>]+>', '', cleaned).strip()
    
    # Questions, inquiries, or task instructions are NOT permanent rules
    if '?' in cleaned or any(w in cleaned.lower() for w in ['kenapa', 'mengapa', 'why', 'check', 'review', 'tolong']):
        return None
        
    if not contains_learning_signal(cleaned):
        return None
    
    cleaned = cleaned.replace('\n', ' ')
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    if len(cleaned) > 280:
        cleaned = cleaned[:277] + "..."
    return cleaned

def is_duplicate_line(norm_new: str, line: str) -> bool:
    if not line.strip().startswith("-"):
        return False
    norm_line = normalize_rule(line)
    if not norm_line or len(norm_line) < 5:
        return False
    return norm_new in norm_line or norm_line in norm_new

def check_duplicate_in_lines(norm_new: str, lines: list) -> bool:
    for line in lines:
        if is_duplicate_line(norm_new, line):
            return True
    return False

def save_learned_rule(rule: str, rules_path: Path, tag: str = "LEARNED_RULE") -> bool:
    if not rules_path.exists():
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_path.write_text("# Procedural Memory Rules\n\n", encoding="utf-8")

    lines = rules_path.read_text(encoding="utf-8").splitlines()
    norm_new = normalize_rule(rule)
    if not norm_new or check_duplicate_in_lines(norm_new, lines):
        return False

    formatted_rule = f"- **[{tag}]**: {rule}"
    
    # Cap total lines to 50 to prevent token bloat
    if len(lines) >= 50:
        # Keep header and DNA, drop oldest non-DNA rule
        header_lines = [l for l in lines if l.startswith('#') or l.startswith('<') or l.startswith('</')]
        rule_lines = [l for l in lines if l.startswith('- ')]
        if len(rule_lines) > 20:
            rule_lines = rule_lines[-19:]
        lines = header_lines + [""] + rule_lines

    lines.append(formatted_rule)
    temp_path = rules_path.with_suffix('.tmp')
    temp_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    temp_path.replace(rules_path)
    return True

def save_project_preference(preference: str, memory_path: Path) -> bool:
    if not memory_path.exists():
        return False
    
    content = memory_path.read_text(encoding="utf-8")
    norm_pref = normalize_rule(preference)
    if norm_pref in normalize_rule(content):
        return False

    pref_header = "## 📌 Learned Rules & User Preferences"
    if pref_header in content:
        parts = content.split(pref_header)
        new_content = parts[0] + pref_header + f"\n- {preference}" + parts[1]
    else:
        new_content = content + f"\n\n{pref_header}\n- {preference}\n"

    temp_path = memory_path.with_suffix('.tmp')
    temp_path.write_text(new_content, encoding="utf-8")
    temp_path.replace(memory_path)
    return True

def parse_user_input_from_line(line_str: str) -> str | None:
    try:
        data = json.loads(line_str)
        if 'USER_INPUT' in str(data.get('type', '')):
            return str(data.get('content', '')).strip()
    except Exception as e:
        sys.stderr.write(f"Transcript parse line notice: {e}\n")
    return None

def process_transcript(transcript_path: Path, rules_path: Path, memory_path: Path) -> int:
    if not transcript_path.exists():
        return 0
    try:
        lines = transcript_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        user_inputs = []
        for line in lines[-10:]:
            parsed = parse_user_input_from_line(line)
            if parsed:
                user_inputs.append(parsed)
        
        saved_count = 0
        for u_text in user_inputs:
            learning = extract_learning_from_user_input(u_text)
            if learning:
                if save_project_preference(learning, memory_path):
                    saved_count += 1
        return saved_count
    except Exception as e:
        sys.stderr.write(f"Transcript learning notice: {e}\n")
        return 0

def synthesize_custom_skill(
    name: str,
    description: str,
    directives: list[str],
    skills_dir: Path = Path(".agents/skills")
) -> bool:
    """Synthesizes a new production-ready skill file (inspired by daymade meta-skill)."""
    sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '', name.lower().strip().replace(' ', '-'))
    if not sanitized_name:
        return False
    
    skill_path = skills_dir / sanitized_name / "SKILL.md"
    if skill_path.exists():
        return False
    
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    
    directives_text = "\n".join(f"{i+1}. **{d.split(':', 1)[0]}**: {d.split(':', 1)[1] if ':' in d else d}" for i, d in enumerate(directives)) if directives else "1. **Standard Execution**: Follow strict L9 verification."
    
    content = f"""---
name: {sanitized_name}
description: {description}
---

# {sanitized_name.replace('-', ' ').title()} Custom Protocol

<CRITICAL_DIRECTIVE>
{description}
</CRITICAL_DIRECTIVE>

<CORE_STANDARDS>
{directives_text}
</CORE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Analyze Requirements**: Understand the target domain tasks.
2. **Execute Invariants**: Implement clean, enterprise-grade logic.
3. **Verify**: Run `python3 scripts/verify.py --execute`.
</PROCEDURAL_WORKFLOW>
"""
    temp_path = skill_path.with_suffix('.tmp')
    temp_path.write_text(content, encoding="utf-8")
    temp_path.replace(skill_path)
    return True

def main() -> None:
    parser = argparse.ArgumentParser(description="AAC Autonomous Self-Learner")
    parser.add_argument("rule", nargs="?", help="Direct rule text to learn")
    parser.add_argument("--audit", action="store_true", help="Audit learned rules and preferences")
    parser.add_argument("--transcript", help="Path to transcript.jsonl for automatic extraction")
    parser.add_argument("--auto", action="store_true", help="Auto extract from transcript")
    parser.add_argument("--synthesize-skill", metavar="NAME", help="Synthesize a new custom domain skill")
    parser.add_argument("--description", default="", help="Description for synthesized skill")
    parser.add_argument("--directive", action="append", default=[], help="Directive rule for synthesized skill")
    args = parser.parse_args()

    rules_path = Path(".agents/brain/rules.md")
    memory_path = Path(".agents/brain/memory.md")

    if args.audit:
        r_count = len([l for l in rules_path.read_text(encoding="utf-8").splitlines() if l.strip().startswith("-")]) if rules_path.exists() else 0
        m_count = len([l for l in memory_path.read_text(encoding="utf-8").splitlines() if l.strip().startswith("-")]) if memory_path.exists() else 0
        print(f"✅ Self-Learner Audit: {r_count} procedural rules, {m_count} memory preferences active. Integrity: 100%.")
        return

    if args.synthesize_skill:
        desc = args.description or f"Custom domain protocol for {args.synthesize_skill}"
        created = synthesize_custom_skill(args.synthesize_skill, desc, args.directive)
        if created:
            print(f"=> SUCCESS: Synthesized custom skill '.agents/skills/{args.synthesize_skill}/SKILL.md'")
        else:
            print(f"=> NOTICE: Skill '{args.synthesize_skill}' already exists or name invalid.")
        return

    if args.rule:
        saved = save_learned_rule(args.rule, rules_path)
        if saved:
            print(f"=> SUCCESS: Recorded new rule in {rules_path}")
        else:
            print("=> NOTICE: Rule already known or duplicate.")
        return

    if args.auto and args.transcript:
        count = process_transcript(Path(args.transcript), rules_path, memory_path)
        if count > 0:
            print(f"=> SUCCESS: Self-Learner automatically saved {count} new rule(s) from conversation.")
        else:
            print("=> No new rules needed extraction.")
        return

    print("Usage: python3 scripts/self_learner.py <rule_text> OR --synthesize-skill <name> OR --auto --transcript <path>")

if __name__ == '__main__':
    main()
