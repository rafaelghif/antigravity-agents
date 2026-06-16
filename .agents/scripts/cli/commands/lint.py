import os
import sys
import subprocess
import utils
import re

def run(args):
    subprojects_file = os.path.join(utils.get_agents_dir(), "subprojects.sh")
    if os.path.exists(subprojects_file):
        try:
            with open(subprojects_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {subprojects_file}: {e}", file=sys.stderr)
            sys.exit(1)
            
        try:
            changed_files = subprocess.check_output(
                ["git", "diff", "--cached", "--name-only"], 
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            changed_files = ""
            
        run_all = 0
        if not changed_files:
            run_all = 1
            print("No staged changes detected. Running linter on all monorepo modules...")
        else:
            print("Analyzing staged file boundaries for monorepo-aware linting...")
            
        failed = 0
        for line in lines:
            line_strip = line.strip()
            if '|' in line_strip:
                clean_line = re.sub(r'^[A-Z_a-z0-9\+]+=\s*\(?\s*', '', line_strip).strip(') \'"')
                parts = clean_line.split('|')
                if len(parts) >= 5:
                    path = parts[0]
                    lint_cmd = parts[4]
                    
                    should_run = run_all
                    if should_run == 0:
                        # check if any changed file starts with path/
                        if any(f.startswith(f"{path}/") for f in changed_files.splitlines()):
                            should_run = 1
                            
                    if should_run == 1:
                        print(f"  Linting {path} ({lint_cmd})...")
                        proc = subprocess.run(lint_cmd, shell=True, cwd=path)
                        if proc.returncode != 0:
                            print(f"  [FAIL] Linter errors found in {path}", file=sys.stderr)
                            failed = 1
                    else:
                        print(f"  Skipping {path} (no staged modifications).")
        sys.exit(failed)
    else:
        rules_file = os.path.join(utils.get_agents_dir(), "rules", "project_rules.md")
        if not os.path.exists(rules_file):
            print("No project rules found.", file=sys.stderr)
            sys.exit(0)
            
        linter_cmd = None
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if "Linter command" in line:
                        m = re.search(r"`([^`]+)`", line)
                        if m:
                            linter_cmd = m.group(1)
                            break
        except Exception as e:
            print(f"Error reading project rules: {e}", file=sys.stderr)
            sys.exit(1)
            
        if linter_cmd and linter_cmd != "echo 'No linter found'":
            print(f"Running linter command: {linter_cmd}...")
            proc = subprocess.run(linter_cmd, shell=True)
            sys.exit(proc.returncode)
        else:
            print("No linter configuration found.")
            sys.exit(0)
