import os
import sys
import re
import utils

def run(args):
    if len(args) == 0:
        print("Usage: helper.py <command> [arguments...]", file=sys.stderr)
        sys.exit(1)
        
    command = args[0]
    
    if command == "create-skill":
        create_skill(args)
    elif command == "list-skills":
        list_skills(args)
    else:
        print(f"Unknown skills command: {command}", file=sys.stderr)
        sys.exit(1)

def create_skill(args):
    if len(args) < 2:
        print("Usage: helper.py create-skill <name> [description]", file=sys.stderr)
        sys.exit(1)
        
    name = args[1]
    desc = args[2] if len(args) > 2 else ""
    
    if not re.match(r"^[a-z0-9-]+$", name):
        print("Error: Skill name must be lowercase kebab-case (e.g., custom-skill-name).", file=sys.stderr)
        sys.exit(1)
        
    workspace_root = utils.find_workspace_root()
    skill_dir = os.path.join(workspace_root, ".agents", "skills", name)
    
    if os.path.exists(skill_dir):
        print(f"Error: Skill '{name}' already exists at {skill_dir}.", file=sys.stderr)
        sys.exit(1)
        
    os.makedirs(os.path.join(skill_dir, "scripts"), exist_ok=True)
    
    skill_md_content = f"""---
name: {name}
description: {desc if desc else f"Specialized skill for {name} automation."}
scripts:
  - scripts/main.py
---

# {name} Skill

## 1. Input Specification
- Specify required inputs (e.g., target file paths, options).

## 2. Operational Procedures
1. Run the associated script.
2. Verify results.

## 3. Decision Matrix
- If the script returns success (exit code 0), the action is accepted.
- If the script returns error, it fails.

## 4. Error Mitigation Tree
- Retry execution.
- If it fails, report details back to the user.

## 5. Output Verification Gate
- [ ] Executable script passes all internal checks.
"""

    script_content = f"""#!/usr/bin/env python3
import argparse
import sys
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_skill(args):
    \"\"\"
    Main logic of the skill script.
    \"\"\"
    logging.info(f"Running skill with arguments: {{args}}")
    # Implement operational logic here
    
    result = {{
        "status": "success",
        "message": "Skill {name} executed successfully",
        "data": {{}}
    }}
    return result

def main():
    parser = argparse.ArgumentParser(description="Default Python script for agent skill {name}.")
    parser.add_argument('--target', type=str, help="Target path or resource")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")
    
    args = parser.parse_args()
    
    try:
        output = run_skill(args)
        print(json.dumps(output, indent=2))
        sys.exit(0)
    except Exception as e:
        logging.error(f"Execution failed: {{str(e)}}")
        error_output = {{
            "status": "error",
            "message": str(e)
        }}
        print(json.dumps(error_output, indent=2))
        sys.exit(1)

if __name__ == '__main__':
    main()
"""

    skill_md_path = os.path.join(skill_dir, "SKILL.md")
    script_path = os.path.join(skill_dir, "scripts", "main.py")
    
    with open(skill_md_path, 'w', encoding='utf-8') as f:
        f.write(skill_md_content)
        
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
        
    os.chmod(script_path, 0o755)
    
    # Scaffold skeleton unit test for the skill
    tests_dir = os.path.join(workspace_root, "tests")
    os.makedirs(tests_dir, exist_ok=True)
    name_with_underscores = name.replace("-", "_")
    test_file_path = os.path.join(tests_dir, f"test_skill_{name_with_underscores}.py")
    
    camel_name = "".join(part.capitalize() for part in name.split("-"))
    test_content = f"""import unittest
import subprocess
import os

class TestSkill{camel_name}(unittest.TestCase):
    def test_help_execution(self):
        \"\"\"Verify that the skill script can be executed with --help.\"\"\"
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            ".agents", "skills", "{name}", "scripts", "main.py"
        )
        self.assertTrue(os.path.exists(script_path), f"Script not found at {{script_path}}")
        
        proc = subprocess.run([sys.executable, script_path, "--help"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)

        self.assertIn("Default Python script for agent skill {name}", proc.stdout)

if __name__ == '__main__':
    unittest.main()
"""
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
        
    print(f"Skill '{name}' created successfully at {skill_dir}")
    print(f"Skeleton unit test scaffolded at {test_file_path}")

def audit_skill(skill_dir):
    skill_name = os.path.basename(skill_dir)
    skill_md = os.path.join(skill_dir, "SKILL.md")
    
    # Check 1: SKILL.md exists
    if not os.path.isfile(skill_md):
        return False, f"{skill_name} is missing SKILL.md"
        
    # Check 2: Parse YAML frontmatter
    try:
        with open(skill_md, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return False, f"failed to read SKILL.md: {e}"
        
    if not lines or lines[0].strip() != "---":
        return False, f"{skill_name} SKILL.md does not start with YAML frontmatter delimiter (---)"
        
    closing_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            closing_idx = i
            break
            
    if closing_idx == -1:
        return False, f"{skill_name} SKILL.md has unclosed YAML frontmatter"
        
    frontmatter_lines = lines[1:closing_idx]
    frontmatter_text = "".join(frontmatter_lines)
    
    # Parse fields
    parsed_name = None
    parsed_desc = None
    for line in frontmatter_lines:
        line_strip = line.strip()
        if line_strip.startswith("name:"):
            parsed_name = line_strip[len("name:"):].strip().strip("'\"")
        elif line_strip.startswith("description:"):
            parsed_desc = line_strip[len("description:"):].strip().strip("'\"")
            
    if not parsed_name:
        return False, f"{skill_name} frontmatter missing 'name'"
    if not parsed_desc:
        return False, f"{skill_name} frontmatter missing 'description'"
        
    # Check 3: Check for placeholders in SKILL.md
    try:
        with open(skill_md, 'r', encoding='utf-8') as f:
            full_content = f.read()
    except Exception as e:
        return False, f"failed to read SKILL.md content: {e}"
        
    if re.search(r"TODO|FIXME|\[placeholder\]", full_content, re.IGNORECASE):
        return False, f"{skill_name} SKILL.md contains placeholder text (TODO/FIXME/placeholder)"
        
    # Check 4: Verify referenced scripts
    in_scripts = False
    script_paths = []
    for line in frontmatter_lines:
        line_strip = line.strip()
        if line_strip.startswith("scripts:"):
            in_scripts = True
            continue
        elif in_scripts and ":" in line_strip and not line_strip.startswith("-"):
            in_scripts = False
            
        if in_scripts:
            if line_strip.startswith("-"):
                script_path_val = line_strip[1:].strip().strip("'\"")
                if script_path_val:
                    script_paths.append(script_path_val)
                    
    for s_path in script_paths:
        full_script_path = os.path.join(skill_dir, s_path)
        if not os.path.isfile(full_script_path):
            return False, f"{skill_name} referenced script {s_path} does not exist"
        if not os.access(full_script_path, os.X_OK):
            return False, f"{skill_name} referenced script {s_path} is not executable (missing chmod +x)"
            
    # Check the scripts directory files if scripts dir exists
    scripts_dir = os.path.join(skill_dir, "scripts")
    if os.path.isdir(scripts_dir):
        for entry in os.listdir(scripts_dir):
            entry_path = os.path.join(scripts_dir, entry)
            if os.path.isfile(entry_path):
                if not os.access(entry_path, os.X_OK):
                    return False, f"{skill_name} script {entry} is not executable"
                try:
                    with open(entry_path, 'r', encoding='utf-8', errors='ignore') as f:
                        script_code = f.read()
                except Exception as e:
                    return False, f"failed to read script {entry}: {e}"
                if re.search(r"TODO|FIXME|\[placeholder\]", script_code, re.IGNORECASE):
                    return False, f"{skill_name} script {entry} contains placeholder text (TODO/FIXME/placeholder)"
                    
    return True, parsed_desc

def list_skills(args):
    skills_dir = os.path.join(utils.get_agents_dir(), "skills")
    if not os.path.isdir(skills_dir):
        print(f"Error: Skills directory {skills_dir} not found.", file=sys.stderr)
        sys.exit(1)
        
    print("==========================================================")
    print("          Antigravity Agent Skills Audit & Registry")
    print("==========================================================")
    
    audit_failed = 0
    print(f"{'Skill Name':<25} | {'Status':<12} | Description")
    print("----------------------------------------------------------")
    
    entries = sorted(os.listdir(skills_dir))
    for entry in entries:
        dir_path = os.path.join(skills_dir, entry)
        if os.path.isdir(dir_path):
            passed, detail = audit_skill(dir_path)
            status = "[PASS]" if passed else "[FAIL]"
            if not passed:
                audit_failed += 1
            print(f"{entry:<25} | {status:<12} | {detail}")
            
    print("==========================================================")
    if audit_failed == 0:
        print("All skills are compliant and ready for use.")
        sys.exit(0)
    else:
        print(f"Audit failed! Found {audit_failed} non-compliant skill(s).", file=sys.stderr)
        sys.exit(1)
