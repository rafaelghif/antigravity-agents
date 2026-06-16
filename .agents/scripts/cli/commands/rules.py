import os
import sys
import re
import utils

def run(args):
    if len(args) == 0:
        print("Usage: helper.py <command> [arguments...]", file=sys.stderr)
        sys.exit(1)
        
    command = args[0]
    
    if command == "create-rule":
        create_rule(args)
    elif command == "list-rules":
        list_rules(args)
    else:
        print(f"Unknown rules command: {command}", file=sys.stderr)
        sys.exit(1)

def create_rule(args):
    if len(args) < 3:
        print("Usage: helper.py create-rule <name> <activation> [description_or_pattern]", file=sys.stderr)
        sys.exit(1)
        
    name = args[1]
    activation = args[2]
    param = args[3] if len(args) > 3 else ""
    
    if not re.match(r"^[a-z0-9-]+$", name):
        print("Error: Rule name must be lowercase kebab-case (e.g., custom-rule-name).", file=sys.stderr)
        sys.exit(1)
        
    activation_mode = ""
    if activation == "manual":
        activation_mode = "Manual"
    elif activation == "always-on":
        activation_mode = "Always On"
    elif activation == "model-decision":
        activation_mode = "Model Decision"
    elif activation == "glob":
        activation_mode = "Glob"
    else:
        print(f"Error: Invalid activation mode '{activation}'. Must be: manual, always-on, model-decision, or glob.", file=sys.stderr)
        sys.exit(1)
        
    pattern = ""
    description = ""
    if activation_mode == "Glob":
        if not param:
            print("Error: Glob activation requires a glob pattern parameter (e.g., 'src/**/*.ts').", file=sys.stderr)
            sys.exit(1)
        pattern = param
    elif activation_mode == "Model Decision":
        if not param:
            print("Error: Model Decision activation requires a natural language description parameter.", file=sys.stderr)
            sys.exit(1)
        description = param
        
    workspace_root = utils.find_workspace_root()
    rule_file = os.path.join(workspace_root, ".agents", "rules", f"{name}.md")
    
    if os.path.exists(rule_file):
        print(f"Error: Rule '{name}' already exists at {rule_file}.", file=sys.stderr)
        sys.exit(1)
        
    os.makedirs(os.path.dirname(rule_file), exist_ok=True)
    
    frontmatter_lines = [
        "---",
        f"name: {name}",
        f"activation: {activation_mode}"
    ]
    if pattern:
        frontmatter_lines.append(f'pattern: "{pattern}"')
    if description:
        frontmatter_lines.append(f'description: "{description}"')
    frontmatter_lines.append("---")
    
    rule_content = "\n".join(frontmatter_lines) + f"""

# {name} Workspace Rule

## Guidelines
- Define the coding standard or instructions for this rule here.
- Example: Prefer arrow functions over traditional function syntax.
"""

    with open(rule_file, 'w', encoding='utf-8') as f:
        f.write(rule_content)
        
    print(f"Rule '{name}' created successfully at {rule_file}")

def audit_rule(rule_file):
    rule_name = os.path.splitext(os.path.basename(rule_file))[0]
    
    if not rule_file.endswith(".md"):
        return False, f"{rule_name} is not a markdown file"
        
    try:
        with open(rule_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return False, f"failed to read rule: {e}"
        
    if not lines or lines[0].strip() != "---":
        return False, f"{rule_name} does not start with YAML frontmatter delimiter (---)"
        
    closing_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            closing_idx = i
            break
            
    if closing_idx == -1:
        return False, f"{rule_name} has unclosed YAML frontmatter"
        
    frontmatter_lines = lines[1:closing_idx]
    
    # Parse fields
    parsed_name = None
    parsed_activation = None
    parsed_pattern = None
    parsed_desc = None
    
    for line in frontmatter_lines:
        line_strip = line.strip()
        if line_strip.startswith("name:"):
            parsed_name = line_strip[len("name:"):].strip().strip("'\"")
        elif line_strip.startswith("activation:"):
            parsed_activation = line_strip[len("activation:"):].strip().strip("'\"")
        elif line_strip.startswith("pattern:"):
            parsed_pattern = line_strip[len("pattern:"):].strip().strip("'\"")
        elif line_strip.startswith("description:"):
            parsed_desc = line_strip[len("description:"):].strip().strip("'\"")
            
    if not parsed_name:
        return False, f"{rule_name} frontmatter missing 'name'"
    if not parsed_activation:
        return False, f"{rule_name} frontmatter missing 'activation'"
        
    if parsed_activation in ("Manual", "Always On"):
        pass
    elif parsed_activation == "Glob":
        if not parsed_pattern:
            return False, f"{rule_name} activation is Glob but missing 'pattern'"
    elif parsed_activation == "Model Decision":
        if not parsed_desc:
            return False, f"{rule_name} activation is Model Decision but missing 'description'"
    else:
        return False, f"{rule_name} has invalid activation mode '{parsed_activation}'"
        
    # Check body for placeholders
    try:
        with open(rule_file, 'r', encoding='utf-8') as f:
            full_content = f.read()
    except Exception as e:
        return False, f"failed to read rule content: {e}"
        
    if re.search(r"TODO|FIXME|\[placeholder\]", full_content, re.IGNORECASE):
        return False, f"{rule_name} contains placeholder text (TODO/FIXME/placeholder)"
        
    # Return activation details
    details = parsed_activation
    if parsed_activation == "Glob":
        details = f"Glob ({parsed_pattern})"
    elif parsed_activation == "Model Decision":
        details = f"Model Decision ({parsed_desc})"
        
    return True, details

def list_rules(args):
    rules_dir = os.path.join(utils.get_agents_dir(), "rules")
    if not os.path.isdir(rules_dir):
        print(f"Error: Rules directory {rules_dir} not found.", file=sys.stderr)
        sys.exit(1)
        
    print("==========================================================")
    print("          Antigravity Agent Rules Audit & Registry")
    print("==========================================================")
    
    audit_failed = 0
    print(f"{'Rule Name':<25} | {'Status':<12} | Activation Mode")
    print("----------------------------------------------------------")
    
    file_found = False
    entries = sorted(os.listdir(rules_dir))
    for entry in entries:
        file_path = os.path.join(rules_dir, entry)
        if os.path.isfile(file_path):
            file_found = True
            passed, detail = audit_rule(file_path)
            status = "[PASS]" if passed else "[FAIL]"
            if not passed:
                audit_failed += 1
            print(f"{entry:<25} | {status:<12} | {detail}")
            
    if not file_found:
        print(f"No rules registered in {rules_dir}.")
        
    print("==========================================================")
    if audit_failed == 0:
        print("All rules are compliant and active.")
        sys.exit(0)
    else:
        print(f"Audit failed! Found {audit_failed} non-compliant rule(s).", file=sys.stderr)
        sys.exit(1)
