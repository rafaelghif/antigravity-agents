import os
import sys
import subprocess
import utils
import re

def run(args):
    subprojects_file = os.path.join(utils.get_agents_dir(), "subprojects.sh")
    if os.path.exists(subprojects_file):
        print("Monorepo detected. Running build compilation...")
        try:
            with open(subprojects_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {subprojects_file}: {e}", file=sys.stderr)
            sys.exit(1)
            
        failed = 0
        for line in lines:
            line_strip = line.strip()
            if '|' in line_strip:
                # remove any array syntax like SUBPROJECTS+=(...)
                clean_line = re.sub(r'^[A-Z_a-z0-9\+]+=\s*\(?\s*', '', line_strip).strip(') \'"')
                parts = clean_line.split('|')
                if len(parts) >= 3:
                    path = parts[0]
                    build_cmd = parts[2]
                    print(f"  Building {path} ({build_cmd})...")
                    proc = subprocess.run(build_cmd, shell=True, cwd=path)
                    if proc.returncode != 0:
                        print(f"  [FAIL] Build failed in {path}", file=sys.stderr)
                        failed = 1
        sys.exit(failed)
    else:
        rules_file = os.path.join(utils.get_agents_dir(), "rules", "project_rules.md")
        if not os.path.exists(rules_file):
            print("No project rules found.", file=sys.stderr)
            sys.exit(0)
            
        build_cmd = None
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if "Build validation" in line:
                        m = re.search(r"`([^`]+)`", line)
                        if m:
                            build_cmd = m.group(1)
                            break
        except Exception as e:
            print(f"Error reading project rules: {e}", file=sys.stderr)
            sys.exit(1)
            
        if build_cmd and build_cmd != "echo 'No build command needed'":
            print(f"Running build command: {build_cmd}...")
            proc = subprocess.run(build_cmd, shell=True)
            sys.exit(proc.returncode)
        else:
            print("No build configuration found.")
            sys.exit(0)
