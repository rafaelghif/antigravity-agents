import sys
import os
import importlib.util

def run(args):
    # Dynamically load the validate.py script located in .agents/scripts/validate.py
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../validate.py'))
    if not os.path.exists(script_path):
        print(f"Error: Validation script not found at '{script_path}'")
        sys.exit(1)
        
    try:
        spec = importlib.util.spec_from_file_location("validate_module", script_path)
        validate_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validate_module)
        validate_module.run_validations()
    except Exception as e:
        print(f"Error executing validation: {e}")
        sys.exit(1)
