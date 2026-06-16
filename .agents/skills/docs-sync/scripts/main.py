#!/usr/bin/env python3
import argparse
import sys
import json
import logging
import os
import re
import ast
import inspect

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_function_signature(node):
    """
    Reconstructs the function signature for a FunctionDef or AsyncFunctionDef node.
    """
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    name = node.name
    
    try:
        args_str = ast.unparse(node.args)
    except:
        args_str = "..."
        
    ret_str = ""
    if node.returns:
        try:
            ret_str = f" -> {ast.unparse(node.returns)}"
        except:
            pass
            
    return f"{prefix} {name}({args_str}){ret_str}"

def parse_python_file(file_path):
    """
    Parses a python file using ast and extracts structural docstrings.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source file '{file_path}' not found.")
        
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()
        
    tree = ast.parse(source_code)
    entries = []
    
    # 1. Module Docstring
    module_doc = ast.get_docstring(tree)
    if module_doc:
        entries.append({
            "type": "module",
            "name": os.path.basename(file_path),
            "docstring": module_doc.strip()
        })
        
    # 2. Walk top-level definitions
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_doc = ast.get_docstring(node)
            if class_doc:
                entries.append({
                    "type": "class",
                    "name": node.name,
                    "docstring": class_doc.strip()
                })
            
            # Methods inside class
            for subnode in node.body:
                if isinstance(subnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_doc = ast.get_docstring(subnode)
                    if method_doc:
                        sig = get_function_signature(subnode)
                        entries.append({
                            "type": "method",
                            "class": node.name,
                            "name": subnode.name,
                            "signature": sig,
                            "docstring": method_doc.strip()
                        })
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_doc = ast.get_docstring(node)
            if func_doc:
                sig = get_function_signature(node)
                entries.append({
                    "type": "function",
                    "name": node.name,
                    "signature": sig,
                    "docstring": func_doc.strip()
                })
                
    return entries

def format_docstring(docstring):
    """
    Cleans and blockquotes a docstring.
    """
    cleaned = inspect.cleandoc(docstring)
    formatted_lines = [f"> {line}" if line.strip() else ">" for line in cleaned.split("\n")]
    return "\n".join(formatted_lines)

def format_entries_to_markdown(entries, file_path):
    """
    Formats extracted AST docstring entries to structured Markdown.
    """
    if not entries:
        return f"> [!NOTE]\n> No docstrings found in `{file_path}`."
        
    lines = []
    for entry in entries:
        t = entry["type"]
        if t == "module":
            lines.append(f"### Module Reference: `{entry['name']}`\n")
            lines.append(format_docstring(entry["docstring"]))
            lines.append("")
        elif t == "class":
            lines.append(f"#### Class: `{entry['name']}`\n")
            lines.append(format_docstring(entry["docstring"]))
            lines.append("")
        elif t == "method":
            lines.append(f"##### Method: `{entry['class']}.{entry['name']}`\n")
            lines.append("```python")
            lines.append(entry["signature"])
            lines.append("```\n")
            lines.append(format_docstring(entry["docstring"]))
            lines.append("")
        elif t == "function":
            lines.append(f"##### Function: `{entry['name']}`\n")
            lines.append("```python")
            lines.append(entry["signature"])
            lines.append("```\n")
            lines.append(format_docstring(entry["docstring"]))
            lines.append("")
            
    return "\n".join(lines).strip()

def run_skill(args):
    """
    Main logic of the docs-sync skill.
    """
    target_path = args.target
    source_path = args.source
    
    if not target_path:
        raise ValueError("Target Markdown file path (--target) is required.")
        
    target_content = ""
    if os.path.exists(target_path):
        with open(target_path, "r", encoding="utf-8") as f:
            target_content = f.read()
    else:
        # If target file doesn't exist, start with an empty string
        logging.info(f"Target file '{target_path}' does not exist. It will be created.")
        
    # Determine the sources to process
    sources_to_process = []
    
    if source_path:
        sources_to_process.append(source_path)
    else:
        # Scan target for any existing start placeholders
        placeholders = re.findall(r"<!--\s*DOCS-SYNC:START\(([^\)]+)\)\s*-->", target_content)
        sources_to_process.extend(placeholders)
        if not sources_to_process:
            logging.info("No placeholders found in target file, and no source file specified. Nothing to sync.")
            return {
                "status": "success",
                "message": "No placeholders or source files processed.",
                "files_synced": []
            }
            
    modified = False
    synced_files = []
    
    for src in sources_to_process:
        logging.info(f"Processing docstring sync for source: '{src}'...")
        
        # Parse and format the docstrings
        try:
            entries = parse_python_file(src)
            formatted_docs = format_entries_to_markdown(entries, src)
        except Exception as e:
            error_msg = f"Failed to sync '{src}': {e}"
            logging.error(error_msg)
            formatted_docs = f"> [!WARNING]\n> {error_msg}"
            
        start_tag = f"<!-- DOCS-SYNC:START({src}) -->"
        end_tag = f"<!-- DOCS-SYNC:END({src}) -->"
        
        # Regex replacement search
        # Matches the start tag, any content between, and the end tag
        pattern = re.compile(
            re.escape(start_tag) + r"(.*?)" + re.escape(end_tag),
            re.DOTALL
        )
        
        replacement = f"{start_tag}\n\n{formatted_docs}\n\n{end_tag}"
        
        if pattern.search(target_content):
            target_content = pattern.sub(lambda m: replacement, target_content)
            modified = True
            synced_files.append(src)
        else:
            # If source was explicitly requested but placeholder was missing, append to target
            if source_path:
                logging.info(f"Placeholder for '{src}' not found. Appending to target file.")
                if target_content and not target_content.endswith("\n"):
                    target_content += "\n"
                target_content += f"\n{replacement}\n"
                modified = True
                synced_files.append(src)
            else:
                logging.warning(f"Start tag found but corresponding end tag '{end_tag}' is missing in target.")
                
    if modified:
        # Write back updated target file
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(target_content)
        logging.info(f"Successfully updated target file: '{target_path}'")
        
    return {
        "status": "success",
        "message": f"Successfully processed docstring synchronization.",
        "files_synced": synced_files
    }

def main():
    parser = argparse.ArgumentParser(description="Synchronize Python docstrings with Markdown documentation.")
    parser.add_argument('--target', '-t', type=str, required=True, help="Target markdown file path")
    parser.add_argument('--source', '-s', type=str, help="Source Python file path (optional)")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        
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
