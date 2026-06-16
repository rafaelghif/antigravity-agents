#!/usr/bin/env python3
import argparse
import sys
import json
import logging
import os
import re
import glob
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_workspace_root():
    """
    Traverse upwards from script directory to find the workspace root.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    curr = script_dir
    while True:
        if os.path.exists(os.path.join(curr, ".agents")):
            return curr
        parent = os.path.dirname(curr)
        if parent == curr:
            return os.path.abspath(os.path.join(script_dir, "..", "..", "..", ".."))
        curr = parent

def prompt_input(prompt_text, default=None, validator=None):
    """
    Prompt the user via console, ensuring valid input and default fallback.
    """
    while True:
        suffix = f" [{default}]" if default else ""
        try:
            val = input(f"{prompt_text}{suffix}: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            sys.exit(1)
            
        if not val and default:
            val = default
            
        if validator:
            if validator(val):
                return val
        elif val:
            return val
            
        print("Invalid input. Please try again.")

def get_next_number(adrs_dir):
    """
    Determine the next ADR sequence number.
    """
    existing_files = glob.glob(os.path.join(adrs_dir, "[0-9][0-9][0-9]-*.md"))
    numbers = []
    for f in existing_files:
        name = os.path.basename(f)
        match = re.match(r"^([0-9]{3})-", name)
        if match:
            numbers.append(int(match.group(1)))
            
    if numbers:
        return max(numbers) + 1
    return 1

def run_skill(args):
    """
    Guided logic to run the ADR wizard.
    """
    workspace_root = find_workspace_root()
    adrs_dir = os.path.join(workspace_root, ".agents", "adrs")
    os.makedirs(adrs_dir, exist_ok=True)
    
    title = args.title
    status = args.status
    context = args.context
    decision = args.decision
    consequences = args.consequences
    
    # If JSON path is specified, load from JSON
    if args.json:
        if not os.path.exists(args.json):
            raise FileNotFoundError(f"JSON input file not found at: {args.json}")
        with open(args.json, "r", encoding="utf-8") as f:
            data = json.load(f)
            title = data.get("title", title)
            status = data.get("status", status)
            context = data.get("context", context)
            decision = data.get("decision", decision)
            consequences = data.get("consequences", consequences)
            
    # Check TTY status to determine if we should fall back to interactive console prompts
    is_interactive = sys.stdin.isatty() and not (title or status or context or decision or consequences or args.json)
    
    if is_interactive:
        print("==========================================================")
        print("          Architectural Decision Record (ADR) Wizard      ")
        print("==========================================================")
        
        title = prompt_input("1. ADR Title (e.g. Enable CORS rules)")
        
        status_validator = lambda s: s.lower() in ("proposed", "accepted", "superseded")
        status = prompt_input("2. Status (proposed/accepted/superseded)", default="proposed", validator=status_validator).lower()
        
        context = prompt_input("3. Context & Problem (What issues are we solving? Alternatives?)")
        decision = prompt_input("4. Decision (What are we committing to?)")
        consequences = prompt_input("5. Consequences (What is the impact/result?)")
        
        print("==========================================================")
    else:
        # Validate inputs are present in non-interactive mode
        if not title:
            raise ValueError("Missing required parameter: --title or --json path")
        if not status:
            status = "proposed"
        status = status.lower()
        if status not in ("proposed", "accepted", "superseded"):
            raise ValueError("Status must be one of: proposed, accepted, superseded")
            
        if not context:
            context = "[No context provided]"
        if not decision:
            decision = "[No decision provided]"
        if not consequences:
            consequences = "[No consequences provided]"
            
    status_cap = status.capitalize()
    
    # Generate index metadata
    num = f"{get_next_number(adrs_dir):03d}"
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    filename = os.path.join(adrs_dir, f"{num}-{slug}.md")
    adr_date = datetime.now().strftime("%Y-%m-%d")
    
    adr_content = f"""# ADR-{num}: {title}

- **Date**: {adr_date}
- **Status**: {status_cap}

## Context
{context}

## Decision
{decision}

## Consequences
{consequences}
"""
    # Write ADR file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(adr_content)
        
    # Register in index map
    index_file = os.path.join(workspace_root, ".agents", "adr.md")
    if os.path.isfile(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            index_content = f.read()
            
        if "## 1. Architectural Decisions Index" not in index_content:
            if not index_content.endswith('\n'):
                index_content += '\n'
            index_content += "\n## 1. Architectural Decisions Index\n"
            
        if not index_content.endswith('\n'):
            index_content += '\n'
            
        index_content += f"- [ADR-{num}: {title}](file://./adrs/{num}-{slug}.md) - Status: {status_cap}\n"
        
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(index_content)
            
    result = {
        "status": "success",
        "message": f"Successfully created and indexed ADR-{num} at {filename}",
        "data": {
            "adr_number": num,
            "title": title,
            "filename": filename,
            "status": status_cap
        }
    }
    return result

def main():
    parser = argparse.ArgumentParser(description="Architectural Decision Record (ADR) guided wizard.")
    parser.add_argument('--title', type=str, help="Title of the ADR")
    parser.add_argument('--status', type=str, help="Status: proposed, accepted, superseded")
    parser.add_argument('--context', type=str, help="ADR Context text block")
    parser.add_argument('--decision', type=str, help="ADR Decision text block")
    parser.add_argument('--consequences', type=str, help="ADR Consequences text block")
    parser.add_argument('--json', type=str, help="Path to JSON file containing ADR metadata")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")
    
    args = parser.parse_args()
    
    try:
        output = run_skill(args)
        print(json.dumps(output, indent=2))
        sys.exit(0)
    except Exception as e:
        logging.error(f"Execution failed: {str(e)}")
        error_output = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(error_output, indent=2))
        sys.exit(1)

if __name__ == '__main__':
    main()
