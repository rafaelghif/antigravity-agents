import sys
import os
from typing import List

def run(args: List[str]) -> None:
    if not args:
        print("Usage: helper.py mcp <register | start>")
        sys.exit(1)
        
    subcommand = args[0].lower()
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../mcp_server.py'))
    
    if not os.path.exists(script_path):
        print(f"[FAIL] MCP server script not found at: {script_path}")
        sys.exit(1)
        
    import importlib.util
    try:
        spec = importlib.util.spec_from_file_location("mcp_server", script_path)
        mcp_server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_server)
    except Exception as e:
        print(f"[FAIL] Failed to load MCP server module: {e}")
        sys.exit(1)
        
    if subcommand == "register":
        force_global = "--global" in args or "-g" in args
        mcp_server.register_server(force_global=force_global)
    elif subcommand == "start":
        mcp_server.start_server()
    else:
        print(f"Unknown MCP subcommand '{subcommand}'. Supported subcommands: register, start.")
        sys.exit(1)
