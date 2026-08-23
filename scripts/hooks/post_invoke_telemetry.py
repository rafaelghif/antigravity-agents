#!/usr/bin/env python3
import sys
import json
import re
from pathlib import Path
from datetime import datetime

def extract_telemetry(transcript_path):
    audit_log = Path('.agents/brain/global_audit.log')
    audit_log.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        content_buffer = []
        with open(transcript_path, 'r') as f:
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
            with audit_log.open('r') as lf:
                exist_lines = lf.readlines()
                if exist_lines:
                    last_line = exist_lines[-1]
                    
        with audit_log.open('a') as af:
            # Another O(N) map instead of loop if we want to avoid for-loops entirely?
            # Actually, `for match in matches:` is a single loop now.
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
    except Exception as e:
        sys.stderr.write(f"Hook wrapper failed: {str(e)}\n")
    
    # Hooks MUST output valid empty JSON
    print("{}")
