#!/usr/bin/env python3
import sys
import json
import re
from pathlib import Path
from datetime import datetime

def update_project_memory():
    memory_path = Path('.agents/brain/memory.md')
    if not memory_path.exists():
        return
    
    stack = []
    # Node detection
    pkg_path = Path('package.json')
    if pkg_path.exists():
        try:
            data = json.loads(pkg_path.read_text(encoding='utf-8'))
            deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            if 'next' in deps: stack.append('Next.js')
            elif 'react' in deps: stack.append('React')
            elif 'vue' in deps: stack.append('Vue')
            if 'tailwindcss' in deps: stack.append('Tailwind CSS')
            if '@tanstack/react-query' in deps or 'react-query' in deps: stack.append('TanStack Query')
            if 'zustand' in deps: stack.append('Zustand')
            if 'prisma' in deps or '@prisma/client' in deps: stack.append('Prisma ORM')
            if 'drizzle-orm' in deps: stack.append('Drizzle ORM')
        except Exception as e:
            sys.stderr.write(f"Package.json analysis notice: {str(e)}\n")

    # Python detection
    if Path('pyproject.toml').exists() or Path('requirements.txt').exists():
        stack.append('Python')

    if stack:
        stack_str = ", ".join(stack)
        try:
            content = memory_path.read_text(encoding='utf-8')
            if 'Auto-detected by agent' in content:
                content = content.replace(
                    '- Framework: Auto-detected by agent',
                    f'- Stack Profile: {stack_str}'
                )
                memory_path.write_text(content, encoding='utf-8')
        except Exception as e:
            sys.stderr.write(f"Memory update notice: {str(e)}\n")

def extract_telemetry(transcript_path):
    audit_log = Path('.agents/brain/global_audit.log')
    audit_log.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        content_buffer = []
        with open(transcript_path, 'r', encoding='utf-8') as f:
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
            with audit_log.open('r', encoding='utf-8') as lf:
                exist_lines = lf.readlines()
                if exist_lines:
                    last_line = exist_lines[-1]
                    
        with audit_log.open('a', encoding='utf-8') as af:
            for match in matches:
                clean_match = match.strip().replace('\n', ' ')
                if clean_match in last_line:
                    continue
                timestamp = datetime.utcnow().isoformat() + "Z"
                af.write(f"[{timestamp}] [TRACE] {clean_match}\n")
                
    except Exception as e:
        sys.stderr.write(f"Telemetry extraction failed: {str(e)}\n")

if __name__ == '__main__':
    try:
        input_data = sys.stdin.read()
        if input_data:
            payload = json.loads(input_data)
            transcript = payload.get('transcriptPath')
            if transcript and Path(transcript).exists():
                extract_telemetry(transcript)
        # Consolidate project memory
        update_project_memory()
    except Exception as e:
        sys.stderr.write(f"Hook wrapper failed: {str(e)}\n")
    
    # Hooks MUST output valid empty JSON
    print("{}")
