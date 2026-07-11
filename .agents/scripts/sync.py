import os
import re
import json

def sync_skills_to_agents_md():
    skills_dir = ".agents/skills"
    agents_file = ".agents/docs/context_map.md"
    
    if not os.path.exists(skills_dir) or not os.path.exists(agents_file):
        print("Warning: Skills directory or context_map.md missing.")
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
        skills_lines.append(f"| `.agents/skills/{s_name}/SKILL.md` | {s_desc} | On match |")
        
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
    print("Successfully synchronized skills index in context_map.md.")

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
    
    # Replace registry under Decisions & ADR Registry only matching consecutive ADR link list
    registry_pattern = r'(## 3\. Decisions & ADR Registry\nAll major architectural changes must be registered as ADRs:\r?\n)((?:- \[.*?\]\(file:\/\/.*?decisions\/.*?\)(?:\r?\n)?)*)'
    new_content = re.sub(registry_pattern, rf"\1{adrs_registry_str}\n", content)
    
    with open(arch_file, 'w', encoding='utf-8') as af:
        af.write(new_content)
    print("Successfully synchronized ADR registry in architecture.md.")

def get_canonical_category(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ["test", "mock", "leak"]):
        return "Testing / Mocking"
    if any(k in t for k in ["path", "os ", "compat", "powershell", "installer"]):
        return "OS Compatibility / PowerShell"
    if any(k in t for k in ["git", "security", "credential", "gpg", "ssh"]):
        return "Git & Security"
    if "performance" in t:
        return "Performance"
    if any(k in t for k in ["token", "context", "restruct", "structure"]):
        return "Workspace Optimization"
    return title.strip()

def sync_lessons_to_rules():
    lessons_file = ".agents/memory/lessons-learned.md"
    rules_file = ".agents/rules.md"
    
    if not os.path.exists(lessons_file) or not os.path.exists(rules_file):
        print("Warning: lessons-learned.md or rules.md missing.")
        return
        
    try:
        with open(lessons_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        parsed_lessons = []
        in_lessons_section = False
        for line in content.split('\n'):
            line_strip = line.strip()
            if line_strip.startswith('## Lessons Learned'):
                in_lessons_section = True
                continue
            elif line_strip.startswith('##') and in_lessons_section:
                break
                
            if in_lessons_section and line_strip.startswith('- '):
                # Extract date if present, e.g. **[2026-07-02]**
                date_match = re.search(r'^\s*-\s+\*\*\[(\d{4}-\d{2}-\d{2})\]\*\*', line)
                date_str = date_match.group(1) if date_match else "1970-01-01"
                
                # Strip prefix bullet and date to get the rest
                rest = re.sub(r'^-\s+(\*\*\[\d{4}-\d{2}-\d{2}\]\*\*\s*)?', '', line_strip)
                
                # Match title/category and description, e.g. **Category**: Description
                match = re.match(r'^\*\*([^*]+)\*\*:\s*(.*)', rest)
                if match:
                    cat = match.group(1).strip()
                    desc = match.group(2).strip()
                    parsed_lessons.append({
                        "date": date_str,
                        "category": cat,
                        "description": desc
                    })
                else:
                    # Fallback if the format is not standard
                    parsed_lessons.append({
                        "date": date_str,
                        "category": "General",
                        "description": rest
                    })
                    
        if not parsed_lessons:
            print("No lessons found in lessons-learned.md to synthesize.")
            return

        # Cluster lessons
        clustered = {} # canonical_category -> {"max_date": str, "descriptions": []}
        for item in parsed_lessons:
            canon_cat = get_canonical_category(item["category"])
            if canon_cat not in clustered:
                clustered[canon_cat] = {
                    "max_date": item["date"],
                    "descriptions": []
                }
            else:
                if item["date"] > clustered[canon_cat]["max_date"]:
                    clustered[canon_cat]["max_date"] = item["date"]
            
            desc = item["description"]
            if desc not in clustered[canon_cat]["descriptions"]:
                clustered[canon_cat]["descriptions"].append(desc)

        # Sort canonical categories by max_date descending
        sorted_categories = sorted(clustered.keys(), key=lambda c: clustered[c]["max_date"], reverse=True)

        active_rules = []
        archived_rules = []
        
        for idx, cat in enumerate(sorted_categories):
            # Keep only the top 2 most recent lessons per category to keep context compact
            descs = clustered[cat]["descriptions"][:2]
            combined_desc = "; ".join(descs)
            rule_str = f"- **[Learning: {cat}]** {combined_desc}"
            if idx < 5:
                active_rules.append(rule_str)
            else:
                archived_rules.append(rule_str)
            
        with open(rules_file, 'r', encoding='utf-8') as f:
            rules_content = f.read()
            
        synthesized_block = "\n## 6. Synthesized Rules (Self-Learning Memory)\n" + "\n".join(active_rules) + "\n"
        
        if "## 6. Synthesized Rules" in rules_content:
            pattern = r'## 6\. Synthesized Rules \(Self-Learning Memory\)[\s\S]*$'
            new_rules_content = re.sub(pattern, synthesized_block.strip() + "\n", rules_content)
        else:
            new_rules_content = rules_content.rstrip() + "\n" + synthesized_block
            
        with open(rules_file, 'w', encoding='utf-8') as f:
            f.write(new_rules_content)
            
        print("Successfully synchronized synthesized rules in rules.md.")

        # Archive pruned rules to historical file
        if archived_rules:
            archive_file = ".agents/memory/lessons-archive.md"
            existing_archive_rules = []
            if os.path.exists(archive_file):
                try:
                    with open(archive_file, 'r', encoding='utf-8') as af:
                        archive_content = af.read()
                    for line in archive_content.split('\n'):
                        line_strip = line.strip()
                        if line_strip.startswith('- **[Learning:'):
                            existing_archive_rules.append(line_strip)
                except Exception:
                    pass
            
            # Merge and deduplicate
            all_archived = list(existing_archive_rules)
            for r in archived_rules:
                if r not in all_archived:
                    all_archived.append(r)
            
            archive_header = """# AAC V3 Lessons Learned Archive

This file stores archived historical lessons learned that have been pruned from the active prompt context to optimize token overhead.

## Archived Lessons
"""
            archive_body = "\n".join(all_archived) + "\n"
            try:
                os.makedirs(os.path.dirname(archive_file), exist_ok=True)
                with open(archive_file, 'w', encoding='utf-8') as af:
                    af.write(archive_header + archive_body)
                print(f"Successfully archived {len(archived_rules)} rules to {archive_file}.")
            except Exception as e:
                print(f"Warning: Failed to write rules archive: {e}")

    except Exception as e:
        print(f"Error synchronizing lessons to rules: {e}")

def sync_skill_validation_hooks():
    skills_dir = ".agents/skills"
    registry_file = ".agents/skills/registry.json"
    
    if not os.path.exists(skills_dir):
        print("Warning: Skills directory missing.")
        return
        
    registry = {"skills": {}}
    for skill_name in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, skill_name)
        if os.path.isdir(skill_path):
            has_validation = os.path.exists(os.path.join(skill_path, "validate.py"))
            has_setup = os.path.exists(os.path.join(skill_path, "setup.sh"))
            registry["skills"][skill_name] = {
                "path": f".agents/skills/{skill_name}",
                "has_validation_hook": has_validation,
                "validation_hook_path": f".agents/skills/{skill_name}/validate.py" if has_validation else None,
                "has_setup": has_setup,
                "setup_path": f".agents/skills/{skill_name}/setup.sh" if has_setup else None
            }
            
    try:
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2)
        print("Successfully synchronized skill validation hooks in skills/registry.json.")
    except Exception as e:
        print(f"Error writing skills registry: {e}")

if __name__ == '__main__':
    sync_skills_to_agents_md()
    sync_adrs_to_architecture_md()
    sync_lessons_to_rules()
    sync_skill_validation_hooks()
