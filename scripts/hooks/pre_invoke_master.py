#!/usr/bin/env python3
import sys
import json
import re
import yaml
from pathlib import Path

def get_context(transcript_path):
    msgs = []
    
    # 1. Long-Term Anchor
    anchor_path = Path('.agents/brain/ANCHOR.md')
    if anchor_path.exists():
        text = anchor_path.read_text().strip()
        if text and text != "(No context yet)":
            msgs.append(f"=== LONG-TERM DAG ANCHOR ===\n{text}")
            
    # 2. Rules
    rules_path = Path('.agents/brain/rules.md')
    if rules_path.exists():
        text = rules_path.read_text().strip()
        if text:
            msgs.append(f"=== SELF-LEARNED RULES ===\n{text}")
            
    # 3. Dynamic Skill Injection
    if transcript_path and Path(transcript_path).exists():
        try:
            with open(transcript_path, 'r') as f:
                first_line = f.readline()
                data = json.loads(first_line)
                # The first step is usually SYSTEM or USER_INPUT containing the system prompt
                sys_prompt = data.get('content', '')
                
                # Check if it contains the YAML frontmatter
                yaml_match = re.search(r'---\n(.*?)\n---', sys_prompt, re.DOTALL)
                if yaml_match:
                    frontmatter = yaml.safe_load(yaml_match.group(1))
                    skills = frontmatter.get('skills', [])
                    if isinstance(skills, list):
                        for skill in skills:
                            skill_path = Path(f'.agents/skills/{skill}/SKILL.md')
                            if skill_path.exists():
                                msgs.append(f"=== INJECTED SKILL: {skill} ===\n{skill_path.read_text().strip()}")
        except Exception as e:
            sys.stderr.write(f"Context extraction failed: {str(e)}\n")

    return "\n\n".join(msgs)

def check_rsi(transcript_path):
    if not transcript_path or not Path(transcript_path).exists():
        return False
        
    try:
        with open(transcript_path, 'r') as f:
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
        sys.stderr.write(f"RSI check failed: {str(e)}\n")
    return False

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            print("{}")
            return
            
        payload = json.loads(input_data)
        transcript_path = payload.get('transcriptPath')
        
        inject_steps = []
        
        # 1. Context Auto-Injection
        context_str = get_context(transcript_path)
        if context_str:
            inject_steps.append({
                "ephemeralMessage": f"SYSTEM AUTO-INJECTION (Do not use view_file/grep_search for these, they are auto-injected to save tokens):\n\n{context_str}"
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
        sys.stderr.write(f"Pre-invoke hook failed: {str(e)}\n")
        print("{}")

if __name__ == '__main__':
    main()
