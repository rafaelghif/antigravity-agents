import sys
import os
import importlib

def main():
    if len(sys.argv) < 2:
        print("Usage: helper.py <command> [args...]")
        print("Available commands: lock, validate, sync, issue, commit, bootstrap")
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    allowed_commands = {'lock', 'validate', 'sync', 'issue', 'commit', 'bootstrap'}
    
    if cmd not in allowed_commands:
        print(f"Error: Unknown command '{cmd}'. Available: {', '.join(allowed_commands)}")
        sys.exit(1)
        
    try:
        # Resolve command file path dynamically
        cmd_file = os.path.abspath(os.path.join(os.path.dirname(__file__), f"commands/{cmd}.py"))
        if not os.path.exists(cmd_file):
            print(f"Error: Command module file '{cmd_file}' not found.")
            sys.exit(1)
            
        # Inject project root path into sys.path to resolve imports correctly
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        if root_path not in sys.path:
            sys.path.insert(0, root_path)
            
        import importlib.util
        spec = importlib.util.spec_from_file_location(f"cmd_{cmd}", cmd_file)
        cmd_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cmd_module)
        cmd_module.run(sys.argv[2:])
    except Exception as e:
        print(f"Error executing command '{cmd}': {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
