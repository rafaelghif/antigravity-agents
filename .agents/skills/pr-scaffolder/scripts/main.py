#!/usr/bin/env python3
import argparse
import sys
import json
import logging
import os
import subprocess
import re

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
            # Fallback
            return os.path.abspath(os.path.join(script_dir, "..", "..", "..", ".."))
        curr = parent

def run_git(args, cwd):
    """
    Run a git command in the specified working directory.
    """
    proc = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr

def resolve_base_branch(workspace_root):
    """
    Extract the active PR target branch from memory.md or fallback.
    """
    memory_path = os.path.join(workspace_root, ".agents", "memory.md")
    if os.path.exists(memory_path):
        try:
            with open(memory_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Look for: - **Active Pull Request Target**: `main`
                match = re.search(r"-\s+\*\*Active Pull Request Target\*\*:\s*`([^`]+)`", content)
                if match:
                    branch = match.group(1).strip()
                    # Verify if branch exists locally or on remote
                    if run_git(["rev-parse", "--verify", "--quiet", branch], cwd=workspace_root)[0] == 0:
                        return branch
                    origin_branch = f"origin/{branch}"
                    if run_git(["rev-parse", "--verify", "--quiet", origin_branch], cwd=workspace_root)[0] == 0:
                        return origin_branch
        except Exception as e:
            logging.warning(f"Failed to read/parse memory.md: {str(e)}")

    # Fallback to upstream branch
    code, out, _ = run_git(["rev-parse", "--abbrev-ref", "@{u}"], cwd=workspace_root)
    if code == 0 and out.strip():
        return out.strip()

    # Fallback to main/origin/main/master/origin/master
    for b in ["main", "origin/main", "master", "origin/master"]:
        if run_git(["rev-parse", "--verify", "--quiet", b], cwd=workspace_root)[0] == 0:
            return b

    return "main"

def get_current_branch(workspace_root):
    """
    Get the name of the current active Git branch.
    """
    code, out, _ = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=workspace_root)
    if code == 0:
        return out.strip()
    return "unknown-branch"

def get_changed_files(workspace_root, base_branch):
    """
    List all changed and added files compared to the base branch.
    """
    code, out, _ = run_git(["diff", base_branch, "--name-only"], cwd=workspace_root)
    if code != 0:
        return []
    
    files = []
    for line in out.splitlines():
        line = line.strip()
        if line and os.path.exists(os.path.join(workspace_root, line)):
            files.append(line)
    return files

def extract_symbol(line):
    """
    Language-agnostic symbol signature extraction from a diff line starting with '+'.
    """
    clean_line = line[1:].strip()
    
    # Ignore comments
    if clean_line.startswith("#") or clean_line.startswith("//") or clean_line.startswith("/*"):
        return None
        
    # Search for keywords at start or word boundary
    match = re.search(r"\b(class|def|func|type|interface|struct|function)\b", clean_line)
    if not match:
        return None
        
    keyword = match.group(1)
    after_keyword = clean_line[match.end():].strip()
    
    # Handle Go receiver, e.g., func (r *Repo) Read()
    if keyword == "func" and after_keyword.startswith("("):
        close_idx = after_keyword.find(")")
        if close_idx != -1:
            after_keyword = after_keyword[close_idx + 1:].strip()
            
    # Extract the first identifier following the keyword/receiver
    ident_match = re.match(r"([a-zA-Z0-9_]+)", after_keyword)
    if ident_match:
        symbol_name = ident_match.group(1)
        return f"{keyword} {symbol_name}"
        
    return None

def extract_symbols_for_file(workspace_root, base_branch, rel_path):
    """
    Get all modified or newly introduced symbols in a specific file.
    """
    code, diff_out, _ = run_git(["diff", base_branch, "-U0", "--", rel_path], cwd=workspace_root)
    if code != 0:
        return []
        
    symbols = []
    for line in diff_out.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            symbol = extract_symbol(line)
            if symbol and symbol not in symbols:
                symbols.append(symbol)
    return symbols

def extract_test_command(workspace_root):
    """
    Read and extract the configured test runner command from project_rules.md.
    """
    rules_path = os.path.join(workspace_root, ".agents", "rules", "project_rules.md")
    if os.path.exists(rules_path):
        try:
            with open(rules_path, "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r"-\s+\*\*Test runner command\*\*:\s*`([^`]+)`", content)
                if match:
                    return match.group(1).strip()
        except Exception as e:
            logging.warning(f"Failed to read project_rules.md: {str(e)}")
    return None

def run_tests(workspace_root, test_cmd):
    """
    Execute the test runner command and capture output verbatim.
    """
    if not test_cmd:
        return "", False, True
        
    logging.info(f"Executing test command: {test_cmd}")
    proc = subprocess.run(test_cmd, shell=True, cwd=workspace_root, capture_output=True, text=True)
    test_logs = proc.stdout + "\n" + proc.stderr
    failed = (proc.returncode != 0)
    return test_logs, failed, False

def get_schema_diff(workspace_root, base_branch):
    """
    Retrieve schema diff from .agents/schemas/ directory.
    """
    code, out, _ = run_git(["diff", base_branch, "--", ".agents/schemas/"], cwd=workspace_root)
    if code == 0:
        return out.strip()
    return ""

def format_local_link(absolute_path):
    """
    Format file path into file:/// URI style with forward slashes.
    """
    formatted = absolute_path.replace("\\", "/")
    if not formatted.startswith("/"):
        formatted = "/" + formatted
    return f"file://{formatted}"

def generate_report(workspace_root, current_branch, base_branch, changed_files, test_cmd, test_logs, test_failed, test_skipped, schema_diff):
    """
    Generate the markdown report contents.
    """
    lines = []
    lines.append(f"# PR Review Guide: {current_branch}")
    lines.append("")
    lines.append(f"This review guide outlines changes on branch `{current_branch}` relative to base branch `{base_branch}`.")
    lines.append("")
    
    # 1. Scope of Work
    lines.append("## 1. Scope of Work")
    if not changed_files:
        lines.append("No file changes detected between current branch and base branch.")
    else:
        lines.append("| File | Local Link | Repo Link | Symbols Modified |")
        lines.append("| --- | --- | --- | --- |")
        for rel_path in sorted(changed_files):
            abs_path = os.path.abspath(os.path.join(workspace_root, rel_path))
            local_link = f"[File (Local)]({format_local_link(abs_path)})"
            repo_link = f"[File (Repo)]({rel_path})"
            
            # Extract symbols
            symbols = extract_symbols_for_file(workspace_root, base_branch, rel_path)
            symbols_str = ", ".join(f"`{s}`" for s in symbols) if symbols else "-"
            
            lines.append(f"| `{rel_path}` | {local_link} | {repo_link} | {symbols_str} |")
            
    lines.append("")
    
    # 2. Verification Logs
    lines.append("## 2. Verification Logs")
    if test_skipped:
        lines.append("> [!NOTE]")
        lines.append("> No active test runner command configured for this workspace.")
    else:
        if test_failed:
            lines.append("> [!WARNING]")
            lines.append("> Verification tests failed!")
        else:
            lines.append("> [!NOTE]")
            lines.append("> Verification tests passed successfully.")
            
        lines.append("")
        lines.append("<details>")
        lines.append("<summary>Click to view verification test logs</summary>")
        lines.append("")
        lines.append("````")
        lines.append(test_logs.strip())
        lines.append("````")
        lines.append("</details>")
        
    lines.append("")
    
    # 3. Schema Changes
    lines.append("## 3. Schema Changes")
    if not schema_diff:
        lines.append("> [!NOTE]")
        lines.append("> No schema changes detected in this branch.")
    else:
        lines.append("```diff")
        lines.append(schema_diff)
        lines.append("```")
        
    lines.append("")
    return "\n".join(lines)

def run_skill(args):
    """
    Main logic coordinator.
    """
    workspace_root = find_workspace_root()
    base_branch = resolve_base_branch(workspace_root)
    current_branch = get_current_branch(workspace_root)
    
    logging.info(f"Targeting base branch: {base_branch}")
    logging.info(f"Current branch: {current_branch}")
    
    # Get changed files
    changed_files = get_changed_files(workspace_root, base_branch)
    
    # Run tests
    test_cmd = extract_test_command(workspace_root)
    test_logs, test_failed, test_skipped = run_tests(workspace_root, test_cmd)
    
    # Get schema diff
    schema_diff = get_schema_diff(workspace_root, base_branch)
    
    # Generate report
    report_content = generate_report(
        workspace_root=workspace_root,
        current_branch=current_branch,
        base_branch=base_branch,
        changed_files=changed_files,
        test_cmd=test_cmd,
        test_logs=test_logs,
        test_failed=test_failed,
        test_skipped=test_skipped,
        schema_diff=schema_diff
    )
    
    # Output path
    # Replace slashes in branch name to form valid filenames
    safe_branch_name = current_branch.replace("/", "_")
    output_dir = os.path.join(workspace_root, ".agents", "workflows")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"pr_review_{safe_branch_name}.md")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    result = {
        "status": "success",
        "message": f"Successfully generated PR review guide at {output_file}",
        "data": {
            "output_file": output_file,
            "base_branch": base_branch,
            "current_branch": current_branch,
            "changed_files_count": len(changed_files),
            "test_status": "failed" if test_failed else ("skipped" if test_skipped else "passed")
        }
    }
    return result

def main():
    parser = argparse.ArgumentParser(description="PR review guide generator.")
    parser.add_argument('--target', type=str, help="Target path or resource")
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
