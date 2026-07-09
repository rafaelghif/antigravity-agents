import sys
import os
import importlib.util

def run(args):
    # Dynamically load the sync.py script located in .agents/scripts/sync.py
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../sync.py'))
    if not os.path.exists(script_path):
        print(f"Error: Sync script not found at '{script_path}'")
        sys.exit(1)
        
    try:
        spec = importlib.util.spec_from_file_location("sync_module", script_path)
        sync_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sync_module)
        sync_module.sync_skills_to_agents_md()
        sync_module.sync_adrs_to_architecture_md()
        sync_module.sync_lessons_to_rules()
        sync_module.sync_skill_validation_hooks()
    except Exception as e:
        print(f"Error executing sync: {e}")
        sys.exit(1)
