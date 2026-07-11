import sys
import os
import json
import platform
import importlib.util
from datetime import datetime

# Initialize and load modules dynamically
scripts_dir = os.path.dirname(os.path.abspath(__file__))

# Resolve scripts directory dynamically to target/workspace if available
cwd_scripts_dir = os.path.abspath(os.path.join(os.getcwd(), '.agents', 'scripts'))
is_valid_workspace = os.path.isdir(cwd_scripts_dir)
if is_valid_workspace:
    target_scripts_dir = cwd_scripts_dir
else:
    target_scripts_dir = scripts_dir
    sys.stderr.write("[INFO] Current working directory is not a valid AAC workspace. Running in idle mode.\n")
    sys.stderr.flush()

token_cmd_file = os.path.join(target_scripts_dir, 'cli', 'commands', 'token.py')
token_cmd = None
if os.path.exists(token_cmd_file):
    try:
        spec = importlib.util.spec_from_file_location("mcp_token_cmd", token_cmd_file)
        token_cmd = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(token_cmd)
    except Exception as e:
        sys.stderr.write(f"Error loading token module from {token_cmd_file}: {e}\n")

# Same for lock command
lock_cmd_file = os.path.join(target_scripts_dir, 'cli', 'commands', 'lock.py')
lock_cmd = None
if os.path.exists(lock_cmd_file):
    try:
        spec = importlib.util.spec_from_file_location("mcp_lock_cmd", lock_cmd_file)
        lock_cmd = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lock_cmd)
    except Exception as e:
        sys.stderr.write(f"Error loading lock module from {lock_cmd_file}: {e}\n")

# Same for validate module
validate_file = os.path.join(target_scripts_dir, 'validate.py')
validate_module = None
if os.path.exists(validate_file):
    try:
        spec = importlib.util.spec_from_file_location("mcp_validate", validate_file)
        validate_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validate_module)
    except Exception as e:
        sys.stderr.write(f"Error loading validate module from {validate_file}: {e}\n")

def list_tools():
    if not is_valid_workspace:
        return {"tools": []}
    return {
        "tools": [
            {
                "name": "log_token_usage",
                "description": "Log prompt and completion tokens for the current task/issue.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt_tokens": {"type": "integer", "description": "Number of prompt tokens consumed"},
                        "completion_tokens": {"type": "integer", "description": "Number of completion tokens consumed"},
                        "task_id": {"type": "string", "description": "Optional task/issue ID. If omitted, auto-detected from branch."}
                    },
                    "required": ["prompt_tokens", "completion_tokens"]
                }
            },
            {
                "name": "get_token_status",
                "description": "Get current daily, monthly, and task token utilization status.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "acquire_module_lock",
                "description": "Acquire module lock for safe collaborative development.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "module_name": {"type": "string", "description": "Name of module to lock"}
                    },
                    "required": ["module_name"]
                }
            },
            {
                "name": "release_module_lock",
                "description": "Release a module lock.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "module_name": {"type": "string", "description": "Name of module to unlock"}
                    },
                    "required": ["module_name"]
                }
            },
            {
                "name": "run_validation",
                "description": "Run the project's local operational compliance audits.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    }

def call_tool(name, arguments):
    if not is_valid_workspace:
        return {"content": [{"type": "text", "text": "Error: Not running inside a valid AAC workspace."}], "isError": True}
    if name == "log_token_usage":
        if not token_cmd:
            return {"content": [{"type": "text", "text": "Error: token command module not loaded."}], "isError": True}
        prompt = arguments.get("prompt_tokens")
        completion = arguments.get("completion_tokens")
        task_id = arguments.get("task_id")
        
        args = [str(prompt), str(completion)]
        if task_id:
            args.extend(["--task", task_id])
            
        # Capture stdout redirecting prints
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            token_cmd.run_log(args)
            output = sys.stdout.getvalue()
            return {"content": [{"type": "text", "text": output.strip()}]}
        except SystemExit as se:
            output = sys.stdout.getvalue()
            return {"content": [{"type": "text", "text": output.strip()}], "isError": se.code != 0}
        finally:
            sys.stdout = old_stdout

    elif name == "get_token_status":
        if not token_cmd:
            return {"content": [{"type": "text", "text": "Error: token command module not loaded."}], "isError": True}
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            token_cmd.run_status([])
            output = sys.stdout.getvalue()
            return {"content": [{"type": "text", "text": output.strip()}]}
        finally:
            sys.stdout = old_stdout

    elif name == "acquire_module_lock":
        if not lock_cmd:
            return {"content": [{"type": "text", "text": "Error: lock command module not loaded."}], "isError": True}
        module_name = arguments.get("module_name")
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            lock_cmd.run([module_name])
            output = sys.stdout.getvalue()
            return {"content": [{"type": "text", "text": output.strip()}]}
        except SystemExit as se:
            output = sys.stdout.getvalue()
            return {"content": [{"type": "text", "text": output.strip()}], "isError": se.code != 0}
        finally:
            sys.stdout = old_stdout

    elif name == "release_module_lock":
        if not lock_cmd:
            return {"content": [{"type": "text", "text": "Error: lock command module not loaded."}], "isError": True}
        module_name = arguments.get("module_name")
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            lock_cmd.run(["--release", module_name])
            output = sys.stdout.getvalue()
            return {"content": [{"type": "text", "text": output.strip()}]}
        except SystemExit as se:
            output = sys.stdout.getvalue()
            return {"content": [{"type": "text", "text": output.strip()}], "isError": se.code != 0}
        finally:
            sys.stdout = old_stdout

    elif name == "run_validation":
        if not validate_module:
            return {"content": [{"type": "text", "text": "Error: validation module not loaded."}], "isError": True}
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            success = validate_module.run_guard()
            output = sys.stdout.getvalue()
            return {"content": [{"type": "text", "text": output.strip()}], "isError": not success}
        finally:
            sys.stdout = old_stdout

    return {"content": [{"type": "text", "text": f"Error: unknown tool {name}"}], "isError": True}

def handle_message(message):
    method = message.get("method")
    msg_id = message.get("id")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "AAC-V3-MCP",
                    "version": "2.144.1"
                }
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": list_tools()
        }
    elif method == "tools/call":
        params = message.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {})
        res = call_tool(name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": res
        }
    elif method == "notifications/initialized" or method.startswith("notifications/"):
        return None
        
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {
            "code": -32601,
            "message": f"Method not found: {method}"
        }
    }

def start_server():
    # Set stdin/stdout binary or line-buffered, preventing custom prints to stdout
    sys.stdout = open(sys.stdout.fileno(), mode='w', buffering=1, encoding='utf-8')
    sys.stdin = open(sys.stdin.fileno(), mode='r', buffering=1, encoding='utf-8')
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            message = json.loads(line)
            response = handle_message(message)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except KeyboardInterrupt:
            break
        except Exception as e:
            sys.stderr.write(f"Error handling MCP line: {e}\n")
            sys.stderr.flush()

def register_server(force_global: bool = False) -> None:
    home = os.path.expanduser("~")
    system = platform.system()
    script_path = os.path.abspath(__file__)
    python_cmd = "python" if platform.system() == "Windows" else "python3"
    
    # 1. Workspace-level config: .agents/mcp_config.json
    workspace_dir = os.path.dirname(os.path.dirname(script_path))
    workspace_config_file = os.path.join(workspace_dir, "mcp_config.json")
    workspace_settings = {}
    if os.path.exists(workspace_config_file):
        try:
            with open(workspace_config_file, 'r', encoding='utf-8') as f:
                workspace_settings = json.load(f)
        except Exception:
            pass
    if "mcpServers" not in workspace_settings:
        workspace_settings["mcpServers"] = {}
    project_root = os.path.dirname(workspace_dir)
    workspace_settings["mcpServers"]["aac-v3-tools"] = {
        "command": python_cmd,
        "args": [os.path.relpath(script_path, project_root)]
    }
    try:
        os.makedirs(os.path.dirname(workspace_config_file), exist_ok=True)
        with open(workspace_config_file, 'w', encoding='utf-8') as f:
            json.dump(workspace_settings, f, indent=2)
        print(f"[OK] Successfully registered MCP server in workspace config:")
        print(f"     File: {workspace_config_file}")
    except Exception as e:
        print(f"[WARN] Failed to write workspace mcp_config.json: {e}")

    if not force_global:
        print("[INFO] Global registration was bypassed to prevent cross-workspace path leakage.")
        print("       To register globally (Cline settings and global config), please run:")
        print("       ./helper.sh mcp register --global")
        return

    # 2. Cline global settings: cline_mcp_settings.json
    if system == "Darwin":
        config_dir = os.path.join(home, "Library", "Application Support", "Code", "User", "globalStorage", "saoudrizwan.claude-dev", "settings")
    elif system == "Windows":
        appdata = os.getenv("APPDATA", os.path.join(home, "AppData", "Roaming"))
        config_dir = os.path.join(appdata, "Code", "User", "globalStorage", "saoudrizwan.claude-dev", "settings")
    else:
        config_dir = os.path.join(home, ".config", "Code", "User", "globalStorage", "saoudrizwan.claude-dev", "settings")
        
    config_file = os.path.join(config_dir, "cline_mcp_settings.json")
    
    settings = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except Exception as e:
            print(f"[FAIL] Could not parse existing settings: {e}")
            sys.exit(1)
            
    if "mcpServers" not in settings:
        settings["mcpServers"] = {}
        
    settings["mcpServers"]["aac-v3-tools"] = {
        "command": python_cmd,
        "args": [script_path],
        "disabled": False,
        "alwaysAllow": True
    }
    
    try:
        os.makedirs(config_dir, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
        print(f"[OK] Successfully registered MCP server 'aac-v3-tools' in Cline settings:")
        print(f"     File: {config_file}")
    except Exception as e:
        print(f"[FAIL] Failed to write Cline settings file: {e}")
        sys.exit(1)

    # 3. Global Antigravity config: ~/.gemini/config/mcp_config.json
    global_config_dir = os.path.join(home, ".gemini", "config")
    global_config_file = os.path.join(global_config_dir, "mcp_config.json")
    global_settings = {}
    if os.path.exists(global_config_file):
        try:
            with open(global_config_file, 'r', encoding='utf-8') as f:
                global_settings = json.load(f)
        except Exception:
            pass
    if "mcpServers" not in global_settings:
        global_settings["mcpServers"] = {}
    global_settings["mcpServers"]["aac-v3-tools"] = {
        "command": python_cmd,
        "args": [script_path]
    }
    try:
        os.makedirs(global_config_dir, exist_ok=True)
        with open(global_config_file, 'w', encoding='utf-8') as f:
            json.dump(global_settings, f, indent=2)
        print(f"[OK] Successfully registered MCP server in global Antigravity config:")
        print(f"     File: {global_config_file}")
    except Exception as e:
        print(f"[WARN] Failed to write global mcp_config.json: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--register", "register"):
        force_global = "--global" in sys.argv or "-g" in sys.argv
        register_server(force_global=force_global)
    else:
        start_server()
