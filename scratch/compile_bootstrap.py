#!/usr/bin/env python3
import os
import re

def compile_bootstrap():
    repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    bootstrap_path = os.path.join(repo_dir, "bootstrap.sh")
    
    if not os.path.exists(bootstrap_path):
        print(f"Error: bootstrap.sh not found at {bootstrap_path}")
        return False
        
    print(f"Reading {bootstrap_path}...")
    with open(bootstrap_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # List of templates to synchronize
    # format: (target_path_in_bootstrap, source_file_path_relative_to_repo)
    templates = [
        ("AGENTS.md", "AGENTS.md"),
        (".agents/memory.md", ".agents/memory.md"),
        (".agents/rules/project_rules.md", ".agents/rules/project_rules.md"),
        (".agents/schema.md", ".agents/schema.md"),
        (".agents/schemas/default_module.md", ".agents/schemas/default_module.md"),
        (".agents/adr.md", ".agents/adr.md"),
        (".agents/adrs/001-initial-workspace-protocol.md", ".agents/adrs/001-initial-workspace-protocol.md"),
        (".agents/adrs/002-introduce-modular-adrs-and-validation.md", ".agents/adrs/002-introduce-modular-adrs-and-validation.md"),
        (".agents/adrs/003-api-key-rotation-and-powershell-wrappers.md", ".agents/adrs/003-api-key-rotation-and-powershell-wrappers.md"),
        (".agents/git_profiles.example", ".agents/git_profiles.example"),
        (".agents/api_keys.example", ".agents/api_keys.example"),
        (".github/workflows/antigravity.yml", ".github/workflows/antigravity.yml"),
        (".agents/skills/codebase-recon/SKILL.md", ".agents/skills/codebase-recon/SKILL.md"),
        (".agents/skills/git-ops/SKILL.md", ".agents/skills/git-ops/SKILL.md"),
        (".agents/skills/test-driven-patch/SKILL.md", ".agents/skills/test-driven-patch/SKILL.md"),
        (".agents/skills/infra-provisioner/SKILL.md", ".agents/skills/infra-provisioner/SKILL.md"),
        (".agents/skills/security-ci-audit/SKILL.md", ".agents/skills/security-ci-audit/SKILL.md"),
        (".agents/skills/code-review/SKILL.md", ".agents/skills/code-review/SKILL.md"),
        (".agents/skills/impact-analysis/SKILL.md", ".agents/skills/impact-analysis/SKILL.md"),
        (".agents/skills/api-rotator/SKILL.md", ".agents/skills/api-rotator/SKILL.md"),
        (".agents/skills/api-rotator/scripts/main.py", ".agents/skills/api-rotator/scripts/main.py"),
        (".agents/scripts/helper.sh", ".agents/scripts/helper.sh"),
        (".agents/scripts/helper.ps1", ".agents/scripts/helper.ps1"),
        (".agents/scripts/recon.sh", ".agents/scripts/recon.sh"),
        (".agents/scripts/validate.sh", ".agents/scripts/validate.sh"),
        (".agents/scripts/api-rotate-wrapper.sh", ".agents/scripts/api-rotate-wrapper.sh"),
        (".agents/scripts/api-rotate-wrapper.ps1", ".agents/scripts/api-rotate-wrapper.ps1"),
        (".agents/scripts/generate-client.js", ".agents/scripts/generate-client.js"),
        (".agents/hooks/pre-commit", ".agents/hooks/pre-commit"),
        (".agents/hooks/post-commit", ".agents/hooks/post-commit"),
        (".agents/hooks/commit-msg", ".agents/hooks/commit-msg"),
    ]
    
    # Check if we need to insert the ADR 002 & 003 template blocks into bootstrap.sh first.
    # They should be written right after 001-initial-workspace-protocol.md.
    if 'write_template_safe ".agents/adrs/002-introduce-modular-adrs-and-validation.md"' not in content:
        print("Inserting .agents/adrs/002-introduce-modular-adrs-and-validation.md block template into bootstrap.sh...")
        adr_001_pattern = r'(write_template_safe "\.agents/adrs/001-initial-workspace-protocol\.md" << \'EOF\'\n.*?\nEOF\n)'
        match = re.search(adr_001_pattern, content, re.DOTALL)
        if match:
            adr_001_block = match.group(1)
            adr_002_block = '\n# 7.2 Write .agents/adrs/002-introduce-modular-adrs-and-validation.md template\nwrite_template_safe ".agents/adrs/002-introduce-modular-adrs-and-validation.md" << \'EOF\'\n# PLACEHOLDER\nEOF\n'
            content = content.replace(adr_001_block, adr_001_block + adr_002_block)
        else:
            print("Warning: Could not locate 001-initial-workspace-protocol.md block to insert ADR 002 template.")
            
    if 'write_template_safe ".agents/adrs/003-api-key-rotation-and-powershell-wrappers.md"' not in content:
        print("Inserting .agents/adrs/003-api-key-rotation-and-powershell-wrappers.md block template into bootstrap.sh...")
        adr_002_pattern = r'(write_template_safe "\.agents/adrs/002-introduce-modular-adrs-and-validation\.md" << \'EOF\'\n.*?\nEOF\n)'
        match = re.search(adr_002_pattern, content, re.DOTALL)
        if match:
            adr_002_block = match.group(1)
            adr_003_block = '\n# 7.2 Write .agents/adrs/003-api-key-rotation-and-powershell-wrappers.md template\nwrite_template_safe ".agents/adrs/003-api-key-rotation-and-powershell-wrappers.md" << \'EOF\'\n# PLACEHOLDER\nEOF\n'
            content = content.replace(adr_002_block, adr_002_block + adr_003_block)
        else:
            print("Warning: Could not locate 002-introduce-modular-adrs-and-validation.md block to insert ADR 003 template.")

    # Check if we need to insert the api_keys.example template block into bootstrap.sh first.
    # It should be written right after git_profiles.example.
    if 'write_template_safe ".agents/api_keys.example"' not in content:
        print("Inserting .agents/api_keys.example block template into bootstrap.sh...")
        # Find the git_profiles.example block
        git_profile_pattern = r'(write_template_safe "\.agents/git_profiles\.example" << \'EOF\'\n.*?\nEOF\n)'
        match = re.search(git_profile_pattern, content, re.DOTALL)
        if match:
            git_profile_block = match.group(1)
            api_keys_template_block = '\n# 7.4 Write .agents/api_keys.example template\nwrite_template_safe ".agents/api_keys.example" << \'EOF\'\n# PLACEHOLDER\nEOF\n'
            content = content.replace(git_profile_block, git_profile_block + api_keys_template_block)
        else:
            print("Warning: Could not locate git_profiles.example block to insert api_keys.example template.")
            
    # Check if we need to insert the api-rotate-wrapper.sh template block into bootstrap.sh first.
    # It should be written right after validate.sh.
    if 'write_template_safe ".agents/scripts/api-rotate-wrapper.sh"' not in content:
        print("Inserting .agents/scripts/api-rotate-wrapper.sh block template into bootstrap.sh...")
        validate_pattern = r'(write_template_safe "\.agents/scripts/validate\.sh" << \'EOF\'\n.*?\nEOF\n)'
        match = re.search(validate_pattern, content, re.DOTALL)
        if match:
            validate_block = match.group(1)
            wrapper_template_block = '\n# Write .agents/scripts/api-rotate-wrapper.sh\nwrite_template_safe ".agents/scripts/api-rotate-wrapper.sh" << \'EOF\'\n# PLACEHOLDER\nEOF\n'
            content = content.replace(validate_block, validate_block + wrapper_template_block)
        else:
            print("Warning: Could not locate validate.sh block to insert api-rotate-wrapper.sh template.")
            
    # Check if we need to insert the api-rotate-wrapper.ps1 template block into bootstrap.sh first.
    # It should be written right after api-rotate-wrapper.sh.
    if 'write_template_safe ".agents/scripts/api-rotate-wrapper.ps1"' not in content:
        print("Inserting .agents/scripts/api-rotate-wrapper.ps1 block template into bootstrap.sh...")
        sh_pattern = r'(write_template_safe "\.agents/scripts/api-rotate-wrapper\.sh" << \'EOF\'\n.*?\nEOF\n)'
        match = re.search(sh_pattern, content, re.DOTALL)
        if match:
            sh_block = match.group(1)
            ps_template_block = '\n# Write .agents/scripts/api-rotate-wrapper.ps1\nwrite_template_safe ".agents/scripts/api-rotate-wrapper.ps1" << \'EOF\'\n# PLACEHOLDER\nEOF\n'
            content = content.replace(sh_block, sh_block + ps_template_block)
        else:
            print("Warning: Could not locate api-rotate-wrapper.sh block to insert api-rotate-wrapper.ps1 template.")
            
    # Check if we need to insert the api-rotator skill blocks into bootstrap.sh first.
    # It should be written right after impact-analysis/SKILL.md.
    if 'write_template_safe ".agents/skills/api-rotator/SKILL.md"' not in content:
        print("Inserting .agents/skills/api-rotator/SKILL.md block template into bootstrap.sh...")
        impact_pattern = r'(write_template_safe "\.agents/skills/impact-analysis/SKILL\.md" << \'EOF\'\n.*?\nEOF\n)'
        match = re.search(impact_pattern, content, re.DOTALL)
        if match:
            impact_block = match.group(1)
            api_rotator_block = '\n# Write .agents/skills/api-rotator/SKILL.md\nwrite_template_safe ".agents/skills/api-rotator/SKILL.md" << \'EOF\'\n# PLACEHOLDER\nEOF\n\n# Write .agents/skills/api-rotator/scripts/main.py\nwrite_template_safe ".agents/skills/api-rotator/scripts/main.py" << \'EOF\'\n# PLACEHOLDER\nEOF\n'
            content = content.replace(impact_block, impact_block + api_rotator_block)
        else:
            print("Warning: Could not locate impact-analysis block to insert api-rotator templates.")
            
    # Also ensure chmod permissions for the rotator main.py script are added to bootstrap.sh
    if 'chmod +x .agents/skills/api-rotator/scripts/main.py' not in content:
        print("Adding chmod +x for api-rotator/scripts/main.py inside bootstrap.sh...")
        content = content.replace(
            'if [ -f .agents/scripts/validate.sh ]; then chmod +x .agents/scripts/validate.sh; fi',
            'if [ -f .agents/scripts/validate.sh ]; then chmod +x .agents/scripts/validate.sh; fi\nif [ -f .agents/skills/api-rotator/scripts/main.py ]; then chmod +x .agents/skills/api-rotator/scripts/main.py; fi'
        )

    # Also ensure chmod permissions for the wrapper script are added to bootstrap.sh
    if 'chmod +x .agents/scripts/api-rotate-wrapper.sh' not in content:
        print("Adding chmod +x for api-rotate-wrapper.sh inside bootstrap.sh...")
        # Insert chmod +x inside setup block
        content = content.replace(
            '            chmod +x .agents/scripts/validate.sh',
            '            chmod +x .agents/scripts/validate.sh\n            chmod +x .agents/scripts/api-rotate-wrapper.sh'
        )
        # Insert chmod +x inside final script check block
        content = content.replace(
            'if [ -f .agents/scripts/validate.sh ]; then chmod +x .agents/scripts/validate.sh; fi',
            'if [ -f .agents/scripts/validate.sh ]; then chmod +x .agents/scripts/validate.sh; fi\nif [ -f .agents/scripts/api-rotate-wrapper.sh ]; then chmod +x .agents/scripts/api-rotate-wrapper.sh; fi'
        )

    # Also ensure gitignore updates are in bootstrap.sh migration logic
    if 'Ignore local agent API key configuration' not in content:
        print("Injecting API key configurations to gitignore template inside bootstrap.sh...")
        old_gitignore_pattern = r'# Ignore local agent git profiles configuration\n\.agents/git_profiles'
        new_gitignore_replacement = '# Ignore local agent git profiles configuration\n.agents/git_profiles\n\n# Ignore local agent API key configuration and active state files\n.agents/api_keys\n.agents/active_api_keys\n.agents/active_api_keys.ps1\n.agents/active_api_profile_name'
        content = re.sub(old_gitignore_pattern, new_gitignore_replacement, content)
        
        # Update migration gitignore checks
        old_migration_check = r'if ! grep -E -q "\^\\.agents/git_profiles" "\$temp_git"; then\n\s+echo -e "\\n# Ignore local agent git profiles configuration\\n\.agents/git_profiles" >> "\$temp_git"\n\s+fi'
        new_migration_replacement = 'if ! grep -E -q "^\\.agents/git_profiles" "$temp_git"; then\n            echo -e "\\n# Ignore local agent git profiles configuration\\n.agents/git_profiles" >> "$temp_git"\n        fi\n        # ensure local API profiles configuration is ignored\n        for ignore_pat in ".agents/api_keys" ".agents/active_api_keys" ".agents/active_api_keys.ps1" ".agents/active_api_profile_name"; do\n            if ! grep -E -q "^$ignore_pat" "$temp_git"; then\n                echo "$ignore_pat" >> "$temp_git"\n            fi\n        done'
        content = re.sub(old_migration_check, new_migration_replacement, content)
        
    for target_path, source_rel_path in templates:
        source_path = os.path.join(repo_dir, source_rel_path)
        if not os.path.exists(source_path):
            print(f"Warning: Source file {source_path} not found. Skipping.")
            continue
            
        print(f"Reading source file {source_rel_path}...")
        with open(source_path, "r", encoding="utf-8") as sf:
            source_content = sf.read()
            
        # Normalize trailing newlines
        if not source_content.endswith("\n"):
            source_content += "\n"
            
        # Escape backslashes if target is CLIENT_GEN_EOF or other specific block, but EOF is literal
        eof_marker = "EOF"
        if "generate-client.js" in target_path:
            eof_marker = "CLIENT_GEN_EOF"
            
        # Escape the file path for regex matching
        escaped_target = re.escape(target_path)
        # Regex to match: write_template_safe "target_path" << 'EOF' ... EOF
        # Using a regex that finds the exact write_template_safe and matches up to the closing EOF
        pattern = r'(write_template_safe "' + escaped_target + r'" << \'' + eof_marker + r'\'\n)(.*?)(\n' + eof_marker + r'\b)'
        
        # Replace content
        match = re.search(pattern, content, re.DOTALL)
        if match:
            print(f"Updating template for {target_path} in bootstrap.sh...")
            # We want to replace group 2 (the placeholder/contents) with source_content
            # To avoid regex escape issues with the replacement content (e.g. \1, \g<1> or backslashes),
            # we use lambda or simple string replacement.
            start_marker = match.group(1)
            end_marker = match.group(3)
            
            full_match_block = match.group(0)
            new_match_block = start_marker + source_content + end_marker
            
            # String replace is safe
            content = content.replace(full_match_block, new_match_block)
        else:
            print(f"Error: Could not locate template block for {target_path} in bootstrap.sh")
            
    print(f"Writing updated {bootstrap_path}...")
    with open(bootstrap_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    # Copy to .agents/bootstrap.sh
    agents_bootstrap_path = os.path.join(repo_dir, ".agents", "bootstrap.sh")
    print(f"Copying to {agents_bootstrap_path}...")
    with open(agents_bootstrap_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Compilation and synchronization successfully completed!")
    return True

if __name__ == "__main__":
    compile_bootstrap()
