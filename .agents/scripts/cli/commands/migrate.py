import os
import sys
import shutil
import subprocess
import utils

def run(args):
    utils.print_title("Antigravity Agent Core - Workspace Migration (V1.9.0)")
    
    backup_suffix = ".backup"
    agents_dir = utils.get_agents_dir()
    
    # 1. Back up files if they exist
    memory_file = utils.get_memory_file()
    if os.path.exists(memory_file):
        print(f"Warning: Existing memory file found. Backing up to {memory_file}{backup_suffix}")
        shutil.copy(memory_file, memory_file + backup_suffix)
        
    project_rules = os.path.join(agents_dir, 'rules', 'project_rules.md')
    if os.path.exists(project_rules):
        print(f"Warning: Existing project rules blueprint found. Backing up to {project_rules}{backup_suffix}")
        shutil.copy(project_rules, project_rules + backup_suffix)
        
    schema_index = os.path.join(agents_dir, 'schema.md')
    if os.path.exists(schema_index):
        print(f"Warning: Existing schema index found. Backing up to {schema_index}{backup_suffix}")
        shutil.copy(schema_index, schema_index + backup_suffix)
        
    # 2. Re-create directory structure
    print("Re-creating directory structure...")
    skills = ['codebase-recon', 'git-ops', 'test-driven-patch', 'infra-provisioner', 'security-ci-audit', 'code-review', 'impact-analysis']
    for s in skills:
        os.makedirs(os.path.join(agents_dir, 'skills', s), exist_ok=True)
        
    os.makedirs(os.path.join(agents_dir, 'workflows'), exist_ok=True)
    os.makedirs(os.path.join(agents_dir, 'archive'), exist_ok=True)
    os.makedirs(os.path.join(agents_dir, 'locks'), exist_ok=True)
    os.makedirs(os.path.join(agents_dir, 'schemas'), exist_ok=True)
    os.makedirs(os.path.join(agents_dir, 'scripts'), exist_ok=True)
    os.makedirs(os.path.join(agents_dir, 'hooks'), exist_ok=True)
    os.makedirs(os.path.join(agents_dir, 'rules'), exist_ok=True)
    
    # 3. Update Git Hooks with custom backup checks
    print("Updating local Git hooks...")
    hooks = ['pre-commit', 'post-commit', 'commit-msg']
    for h in hooks:
        src_hook = os.path.join(agents_dir, 'hooks', h)
        dest_hook = os.path.join('.git', 'hooks', h)
        if os.path.exists(src_hook):
            # Check if custom hooks exist and backup if not ours
            if os.path.exists(dest_hook):
                is_ours = False
                try:
                    with open(dest_hook, 'r') as f:
                        if "Antigravity Agent Git Hook" in f.read():
                            is_ours = True
                except: pass
                
                if not is_ours:
                    print(f"  - Backing up existing custom {h} hook")
                    shutil.move(dest_hook, dest_hook + ".backup")
                    
            shutil.copy(src_hook, dest_hook)
            try:
                os.chmod(dest_hook, 0o755)
            except: pass
            print(f"  - Installed {h} hook")
            
    # 4. Update memory.md schema version
    if os.path.exists(memory_file):
        print("Updating memory ledger schema version to 5.0.0...")
        try:
            with open(memory_file, 'r') as f:
                content = f.read()
            if "Memory Schema Version" in content:
                import re
                content = re.sub(r"Memory Schema Version\*\*: [0-9]+\.[0-9]+\.[0-9]+", "Memory Schema Version**: 5.0.0", content)
            else:
                header = "# Agent Core Memory\n\n> **Memory Schema Version**: 5.0.0  \n> **Target System**: Antigravity Agent Core\n> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.\n\n"
                # skip first line if it's the title
                lines = content.splitlines()
                if lines and lines[0].startswith("# "):
                    content = header + "\n".join(lines[1:])
                else:
                    content = header + content
            with open(memory_file, 'w') as f:
                f.write(content)
        except Exception as e:
            print(f"Warning: Failed to update memory schema version: {e}", file=sys.stderr)
            
    # 5. Fix .gitignore configuration
    gitignore = ".gitignore"
    if os.path.exists(gitignore):
        print("Validating .gitignore compliance...")
        try:
            with open(gitignore, 'r') as f:
                content = f.read()
            block = """# <<< ANTIGRAVITY AGENT START >>>
# Ignore agent transient locks
.agents/locks/

# Ignore local agent API key configuration and active state files
.agents/api_keys
.agents/active_api_keys
.agents/active_api_keys.ps1
.agents/active_api_profile_name
# <<< ANTIGRAVITY AGENT END >>>"""

            start_guard = '# <<< ANTIGRAVITY AGENT START >>>'
            end_guard = '# <<< ANTIGRAVITY AGENT END >>>'
            
            ignored_patterns = {
                '.agents', '.agents/', 'AGENTS.md', '.agents/locks/', '.agents/locks',
                '.agents/git_profiles', '.agents/api_keys', '.agents/active_api_keys',
                '.agents/active_api_keys.ps1', '.agents/active_api_profile_name'
            }
            
            lines = content.splitlines()
            lines = [l for l in lines if l.strip() not in ignored_patterns]
            content = '\n'.join(lines) + '\n'
            
            if start_guard in content and end_guard in content:
                start_idx = content.find(start_guard)
                end_idx = content.find(end_guard) + len(end_guard)
                new_content = content[:start_idx] + block + content[end_idx:]
            else:
                if not content.endswith('\n'):
                    content += '\n'
                new_content = content + '\n' + block + '\n'
                
            while new_content.endswith('\n\n'):
                new_content = new_content[:-1]
                
            with open(gitignore, 'w') as f:
                f.write(new_content)
            print("  - .gitignore updated with Antigravity Agent block guards.")
        except Exception as e:
            print(f"Warning: Failed to update .gitignore: {e}", file=sys.stderr)
    else:
        print("Creating default compliant .gitignore...")
        try:
            with open(gitignore, 'w') as f:
                f.write("""# <<< ANTIGRAVITY AGENT START >>>
# Ignore agent transient locks
.agents/locks/

# Ignore local agent API key configuration and active state files
.agents/api_keys
.agents/active_api_keys
.agents/active_api_keys.ps1
.agents/active_api_profile_name
# <<< ANTIGRAVITY AGENT END >>>
""")
        except Exception as e:
            print(f"Warning: Failed to create default .gitignore: {e}", file=sys.stderr)
            
    # 6. Re-run stack discovery
    print("Running autonomous stack reconstruction...")
    recon_sh = os.path.join(agents_dir, 'scripts', 'recon.sh')
    if os.path.exists(recon_sh):
        subprocess.run([recon_sh, "-f"])
        
    print("==========================================================")
    print("Migration Complete! Workspace successfully upgraded.")
    print("==========================================================")
