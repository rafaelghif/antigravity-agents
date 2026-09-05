#!/usr/bin/env python3
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from hook_utils import read_safe_stdin
except ImportError:
    from scripts.hooks.hook_utils import read_safe_stdin

def update_project_memory() -> None:
    memory_path = ROOT / '.agents' / 'brain' / 'memory.md'
    if not memory_path.exists():
        return
    try:
        from scripts.grounding import detect_ecosystems
        ecosystems = detect_ecosystems(ROOT)
        if ecosystems:
            stack_str = ", ".join(sorted(ecosystems.keys()))
            content = memory_path.read_text(encoding='utf-8')
            if 'Auto-detected by agent' in content:
                content = content.replace(
                    '- Framework: Auto-detected by agent',
                    f'- Stack Profile: {stack_str}'
                )
                memory_path.write_text(content, encoding='utf-8')
    except Exception as e:
        sys.stderr.write(f"Memory update notice: {str(e)}\n")

def extract_telemetry(transcript_path: str) -> None:
    audit_log = ROOT / '.agents' / 'brain' / 'global_audit.log'
    audit_log.parent.mkdir(parents=True, exist_ok=True)
    
    # Cap log size to 1MB to prevent runaway file size
    if audit_log.exists() and audit_log.stat().st_size > 1_000_000:
        try:
            audit_log.write_text("", encoding='utf-8')
        except OSError as e:
            sys.stderr.write(f"Log truncation notice: {e}\n")
    
    try:
        content_buffer = []
        with open(transcript_path, 'r', encoding='utf-8', newline='') as f:
            lines = f.readlines()
            
        def process_line(line_str):
            data = json.loads(line_str)
            if 'thinking' in data:
                return data['thinking']
            if 'content' in data:
                return data['content']
            return ""
            
        # O(N) map instead of nested loop
        contents = list(map(lambda l: process_line(l) if l.strip() else "", lines))
        full_text = " ".join([c for c in contents if isinstance(c, str)])
        
        matches = re.findall(r'<telemetry>(.*?)</telemetry>', full_text, re.DOTALL)
        
        last_line = ""
        if audit_log.exists():
            with audit_log.open('r', encoding='utf-8', newline='') as lf:
                exist_lines = lf.readlines()
                if exist_lines:
                    last_line = exist_lines[-1]
                    
        with audit_log.open('a', encoding='utf-8', newline='') as af:
            for match in matches:
                clean_match = match.strip().replace('\n', ' ')
                if clean_match in last_line:
                    continue
                timestamp = datetime.now(timezone.utc).isoformat()
                af.write(f"[{timestamp}] [TRACE] {clean_match}\n")
                
    except Exception as e:
        sys.stderr.write(f"Telemetry extraction failed: {str(e)}\n")

if __name__ == '__main__':
    try:
        input_data = read_safe_stdin()
        if input_data:
            payload = json.loads(input_data)
            transcript = payload.get('transcriptPath')
            if transcript and Path(transcript).exists():
                extract_telemetry(transcript)
                try:
                    from scripts.memory_consolidator import sync_transcript_to_memory
                    sync_transcript_to_memory(Path(transcript))
                except Exception as e:
                    sys.stderr.write(f"Memory consolidator hook notice: {e}\n")
                try:
                    from scripts.self_learner import process_transcript
                    rules_path = ROOT / ".agents" / "brain" / "rules.md"
                    memory_path = ROOT / ".agents" / "brain" / "memory.md"
                    process_transcript(Path(transcript), rules_path, memory_path)
                except Exception as e:
                    sys.stderr.write(f"Self-learner hook notice: {e}\n")
        # Consolidate project memory
        update_project_memory()
        # Auto-clean lingering scratch files
        try:
            from scripts.git_hygiene_guard import clean_scratch_files
            clean_scratch_files(ROOT)
        except Exception as e:
            sys.stderr.write(f"Scratch auto-clean notice: {str(e)}\n")
    except Exception as e:
        sys.stderr.write(f"Hook wrapper failed: {str(e)}\n")
    
    # Hooks MUST output valid empty JSON
    print("{}")
