import os
import re

def sync_skills_to_agents_md():
    skills_dir = ".agents/skills"
    agents_file = "AGENTS.md"
    
    if not os.path.exists(skills_dir) or not os.path.exists(agents_file):
        print("Warning: Skills directory or AGENTS.md missing.")
        return
        
    skills = []
    for skill_name in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, skill_name, "SKILL.md")
        if os.path.exists(skill_path):
            try:
                with open(skill_path, 'r', encoding='utf-8') as sf:
                    content = sf.read()
                    # Parse YAML frontmatter
                    m_desc = re.search(r'description:\s*(.*?)\n', content)
                    desc = m_desc.group(1).strip() if m_desc else "No description provided."
                    skills.append((skill_name, desc))
            except Exception:
                pass
                
    # Sort skills by name
    skills.sort()
    
    with open(agents_file, 'r', encoding='utf-8') as af:
        content = af.read()
        
    # Build the new skills table block
    skills_lines = []
    for s_name, s_desc in skills:
        skills_lines.append(f"| `.agents/skills/{s_name}/SKILL.md` | {s_desc} | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |")
        
    skills_table_str = "\n".join(skills_lines)
    
    # Replace in Context Map table
    # We find the table rows matching `.agents/skills/.../SKILL.md`
    # Let's replace the whole table cleanly
    table_pattern = r'(\| `\.agents/skills/\*/SKILL\.md` \| .*? \| Always.*?\n|\| `\.agents/skills/.*?/SKILL\.md` \| .*?\n)+'
    if re.search(table_pattern, content):
        content = re.sub(table_pattern, skills_table_str + "\n", content)
    else:
        # Fallback: find standard skills line and replace it
        fallback_pattern = r'\| `\.agents/skills/\*/SKILL\.md` \|.*?\n'
        content = re.sub(fallback_pattern, skills_table_str + "\n", content)
        
    with open(agents_file, 'w', encoding='utf-8') as af:
        af.write(content)
    print("Successfully synchronized skills index in AGENTS.md.")

def sync_adrs_to_architecture_md():
    adrs_dir = ".agents/memory/decisions"
    arch_file = ".agents/memory/architecture.md"
    
    if not os.path.exists(adrs_dir) or not os.path.exists(arch_file):
        print("Warning: ADR decisions directory or architecture.md missing.")
        return
        
    adrs = []
    for adr_file in os.listdir(adrs_dir):
        if adr_file.endswith(".md"):
            adr_path = os.path.join(adrs_dir, adr_file)
            try:
                with open(adr_path, 'r', encoding='utf-8') as f:
                    title_line = f.readline().strip("# \n")
                    adrs.append((adr_file, title_line))
            except Exception:
                pass
                
    # Sort ADRs
    adrs.sort()
    
    with open(arch_file, 'r', encoding='utf-8') as af:
        content = af.read()
        
    adrs_lines = []
    for a_file, a_title in adrs:
        adrs_lines.append(f"- [{a_title}](file://./decisions/{a_file})")
        
    adrs_registry_str = "\n".join(adrs_lines)
    
    # Replace registry under Decisions & ADR Registry
    registry_pattern = r'(## 3\. Decisions & ADR Registry\nAll major architectural changes must be registered as ADRs:\n)([\s\S]*?)$'
    new_content = re.sub(registry_pattern, rf"\1{adrs_registry_str}\n", content)
    
    with open(arch_file, 'w', encoding='utf-8') as af:
        af.write(new_content)
    print("Successfully synchronized ADR registry in architecture.md.")

if __name__ == '__main__':
    sync_skills_to_agents_md()
    sync_adrs_to_architecture_md()
