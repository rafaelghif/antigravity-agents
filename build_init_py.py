import os
import re

def main():
    helper_path = "/home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/helper.sh"
    with open(helper_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # We want to process lines from line 284 to 2725 (0-indexed: 283 to 2724)
    # Let's map sections by line numbers (1-indexed, so we compare with line_num = idx + 1)
    # Next.js: 455 to 680
    # Go Gin: 681 to 840
    # FastAPI: 841 to 929
    # Monorepo: 930 to 1358
    # Multi-Project: 1359 to 1688
    # Laravel: 1689 to 2205
    # Fallback: 2206 to 2267
    # Docker: 2268 to 2725
    
    sections = {
        "Next.js": [],
        "Go Gin": [],
        "FastAPI": [],
        "Monorepo": [],
        "Multi-Project": [],
        "Laravel": [],
        "Fallback": [],
        "Docker": []
    }
    
    i = 283
    while i < 2725:
        line_num = i + 1
        line = lines[i]
        line_strip = line.strip()
        
        # Determine section
        if 455 <= line_num <= 680:
            section = "Next.js"
        elif 681 <= line_num <= 840:
            section = "Go Gin"
        elif 841 <= line_num <= 929:
            section = "FastAPI"
        elif 930 <= line_num <= 1358:
            section = "Monorepo"
        elif 1359 <= line_num <= 1688:
            section = "Multi-Project"
        elif 1689 <= line_num <= 2205:
            section = "Laravel"
        elif 2206 <= line_num <= 2267:
            section = "Fallback"
        elif 2268 <= line_num <= 2725:
            section = "Docker"
        else:
            section = None
            
        if section:
            # Parse mkdir -p
            mkdir_match = re.match(r"^mkdir\s+-p\s+(.+)$", line_strip)
            if mkdir_match:
                dirs = mkdir_match.group(1).strip().split()
                sections[section].append({
                    "type": "mkdir",
                    "dirs": dirs,
                    "line_num": line_num,
                    "raw": line_strip
                })
                
            # Parse cat << (redirect or assignment)
            cat_match = re.search(r"(?:([a-zA-Z0-9_]+)=)?\s*\$?\(\s*cat\s+<<\s+['\"]?([a-zA-Z0-9_]+)['\"]?|cat\s+<<\s+['\"]?([a-zA-Z0-9_]+)['\"]?\s*>\s*(>?)\s*(.+)$", line_strip)
            if cat_match:
                # Group 1: variable name (if assignment)
                # Group 2: marker (if assignment)
                # Group 3: marker (if redirect)
                # Group 4: is_append (if redirect)
                # Group 5: filepath (if redirect)
                
                is_assign = cat_match.group(2) is not None
                var_name = cat_match.group(1) if is_assign else None
                marker = cat_match.group(2) if is_assign else cat_match.group(3)
                is_append = (cat_match.group(4) == ">") if not is_assign else False
                filepath = cat_match.group(5).strip().strip('"\'') if not is_assign else None
                
                i += 1
                content_lines = []
                while i < len(lines):
                    curr_line = lines[i]
                    # Check if line ends with the marker (e.g. "DB_POSTGRES" or "DB_POSTGRES)" or "DB_POSTGRES )")
                    curr_strip = curr_line.strip()
                    if curr_strip == marker or curr_strip == f"{marker})" or curr_strip.startswith(f"{marker}") and curr_strip.endswith(")"):
                        break
                    content_lines.append(curr_line)
                    i += 1
                
                content = "".join(content_lines)
                sections[section].append({
                    "type": "variable_assignment" if is_assign else "write_file",
                    "variable": var_name,
                    "path": filepath,
                    "content": content,
                    "append": is_append,
                    "line_num": line_num,
                    "raw": line_strip
                })
        i += 1

    import json
    with open("/home/rafaelghifari/Muraghi/Project/antigravity-agent/extracted_sections.json", "w", encoding="utf-8") as out:
        json.dump(sections, out, indent=2)
        
    print("Extracted sections saved to extracted_sections.json")

if __name__ == "__main__":
    main()
