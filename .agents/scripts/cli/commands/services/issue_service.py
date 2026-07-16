import os
import sys
import re
import subprocess
from datetime import datetime

try:
    from core.logger import logger
except ImportError:
    try:
        from ....core.logger import logger
    except ImportError:
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
        from core.logger import logger

# Inject parent directory containing git_api
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)


ISSUE_DIR = ".agents/issues"

def parse_issue_frontmatter(content):
    lines = content.splitlines()
    fm = {}
    if len(lines) > 0 and lines[0].strip() == '---':
        fm_lines = []
        for line in lines[1:]:
            if line.strip() == '---':
                break
            fm_lines.append(line)
        for line in fm_lines:
            if ':' in line:
                k, v = line.split(':', 1)
                k = k.strip()
                v = v.strip()
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                fm[k] = v

    if fm.get("id") or fm.get("title"):
        try:
            from core.entities import Issue, ValidationError
        except ImportError:
            try:
                from ....core.entities import Issue, ValidationError
            except ImportError:
                sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
                from core.entities import Issue, ValidationError
        try:
            issue_entity = Issue.from_dict(fm)
            issue_entity.validate()
        except ValidationError as ve:
            logger.warn(f"Issue frontmatter validation failed: {ve}")

    return fm

def get_issue_tasks(content):
    lines = content.splitlines()
    all_tasks = []
    unchecked = []
    in_relevant_section = False
    
    for line in lines:
        striped = line.strip()
        if striped.startswith('##'):
            lower_header = striped.lower()
            if 'task' in lower_header or 'subtask' in lower_header or 'criteria' in lower_header:
                in_relevant_section = True
            else:
                in_relevant_section = False
        elif in_relevant_section:
            if striped.startswith(('-', '*')) and '[' in striped and ']' in striped:
                match = re.match(r'^[-*]\s*\[\s*([xX\s/])\s*\]\s+(.*)', striped)
                if match:
                    all_tasks.append(striped)
                    if match.group(1).strip() == '':
                        unchecked.append(striped)
    return all_tasks, unchecked

def update_board_completed(issue_id):
    board_path = ".agents/tasks/board.md"
    if not os.path.exists(board_path):
        return
    try:
        with open(board_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.splitlines()
        target_line = None
        new_lines = []
        
        pattern = rf"<!-- id:\s*{re.escape(issue_id)}\s*-->"
        for line in lines:
            if re.search(pattern, line):
                target_line = line
            else:
                new_lines.append(line)
                
        if target_line:
            target_line = re.sub(r'\[\s*\]', '[x]', target_line)
            target_line = re.sub(r'\[\s*[xX]\s*\]', '[x]', target_line)
            target_line = re.sub(r'\[\s*/\s*\]', '[x]', target_line)
            
            done_idx = -1
            for idx, line in enumerate(new_lines):
                if line.strip() == "## Done":
                    done_idx = idx
                    break
            
            if done_idx != -1:
                new_lines.insert(done_idx + 1, target_line)
            else:
                new_lines.append(target_line)
                
            with open(board_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(new_lines) + "\n")
            logger.success(f"Moved task '{issue_id}' to Done in task board.")
    except Exception as e:
        logger.warn(f"Could not update task board: {e}")

def sync_board_with_issues():
    board_path = ".agents/tasks/board.md"
    if not os.path.exists(board_path):
        return
    try:
        issues = []
        if os.path.exists(ISSUE_DIR):
            for f_name in os.listdir(ISSUE_DIR):
                if f_name.endswith(".md") and not "example" in f_name:
                    issues.append(os.path.join(ISSUE_DIR, f_name))
        archive_dir = ".agents/archive/issues"
        if os.path.exists(archive_dir):
            for f_name in os.listdir(archive_dir):
                if f_name.endswith(".md"):
                    issues.append(os.path.join(archive_dir, f_name))

        issue_data = {}
        for path in issues:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                fm = parse_issue_frontmatter(content)
                i_id = fm.get("id")
                title = fm.get("title")
                status = fm.get("status", "open")
                if i_id and title:
                    issue_data[i_id.lower()] = {
                        "id": i_id,
                        "title": title,
                        "status": status.lower()
                    }
            except Exception:
                pass

        with open(board_path, 'r', encoding='utf-8') as f:
            board_content = f.read()

        lines = board_content.splitlines()
        
        todo_lines = []
        doing_lines = []
        done_lines = []
        header_lines = []
        footer_lines = []
        
        current_section = "header"
        for line in lines:
            stripped = line.strip()
            if stripped == "## Todo":
                current_section = "todo"
                header_lines.append(line)
                continue
            elif stripped == "## Doing":
                current_section = "doing"
                header_lines.append(line)
                continue
            elif stripped == "## Done":
                current_section = "done"
                header_lines.append(line)
                continue
            elif stripped.startswith("## ") and current_section in ("todo", "doing", "done"):
                current_section = "footer"
                footer_lines.append(line)
                continue
                
            if current_section == "header":
                header_lines.append(line)
            elif current_section == "footer":
                footer_lines.append(line)
            elif current_section == "todo":
                if stripped.startswith("- ["):
                    todo_lines.append(line)
                elif stripped:
                    todo_lines.append(line)
            elif current_section == "doing":
                if stripped.startswith("- ["):
                    doing_lines.append(line)
                elif stripped:
                    doing_lines.append(line)
            elif current_section == "done":
                if stripped.startswith("- ["):
                    done_lines.append(line)
                elif stripped:
                    done_lines.append(line)

        board_ids = {}
        def extract_id(line):
            match = re.search(r'<!-- id:\s*([a-zA-Z0-9_-]+)\s*-->', line)
            return match.group(1).lower() if match else None

        all_board_lines = todo_lines + doing_lines + done_lines
        for line in all_board_lines:
            i_id = extract_id(line)
            if i_id:
                board_ids[i_id] = line

        updated_todo = []
        updated_doing = []
        updated_done = []
        processed_ids = set()

        for line in all_board_lines:
            i_id = extract_id(line)
            if not i_id or i_id not in issue_data:
                if line in todo_lines:
                    updated_todo.append(line)
                elif line in doing_lines:
                    updated_doing.append(line)
                elif line in done_lines:
                    updated_done.append(line)
                continue
                
            processed_ids.add(i_id)
            info = issue_data[i_id]
            status = info["status"]
            
            if status in ("closed", "done"):
                new_line = re.sub(r'\[\s*.*?\]', '[x]', line)
                updated_done.append(new_line)
            else:
                if line in doing_lines:
                    updated_doing.append(line)
                else:
                    new_line = re.sub(r'\[\s*xX\s*\]', '[ ]', line)
                    updated_todo.append(new_line)

        for i_id, info in issue_data.items():
            if i_id not in processed_ids:
                status = info["status"]
                title = info["title"]
                slug = info["id"].lower().replace('_', '-')
                branch_name = f"feat/{slug}"
                
                if status in ("closed", "done"):
                    new_line = f"- [x] {title} ({branch_name}) <!-- id: {info['id']} -->"
                    updated_done.append(new_line)
                else:
                    new_line = f"- [ ] {title} ({branch_name}) <!-- id: {info['id']} -->"
                    updated_todo.append(new_line)

        output = []
        for line in header_lines:
            output.append(line)
            if line.strip() == "## Todo":
                output.extend(updated_todo)
                if not updated_todo:
                    output.append("")
            elif line.strip() == "## Doing":
                output.extend(updated_doing)
                if not updated_doing:
                    output.append("")
            elif line.strip() == "## Done":
                output.extend(updated_done)
                if not updated_done:
                    output.append("")

        output.extend(footer_lines)

        with open(board_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(output) + "\n")
        logger.success("Task board (board.md) successfully synchronized with issue states.")
    except Exception as e:
        logger.warn(f"Could not sync task board: {e}")

def sync_issues():
    try:
        import git_api
        remote_issues = git_api.fetch_github_issues()
        if remote_issues is None:
            logger.info("Operating in local offline mode using local issue cache.")
            return
            
        logger.info("Synchronizing local issues with GitHub remote...")
        if not os.path.exists(ISSUE_DIR):
            os.makedirs(ISSUE_DIR, exist_ok=True)
            
        local_issues = {}
        for f_name in os.listdir(ISSUE_DIR):
            if not f_name.endswith(".md") or "example" in f_name:
                continue
            path = os.path.join(ISSUE_DIR, f_name)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                fm = parse_issue_frontmatter(content)
                if "github_number" in fm:
                    local_issues[int(fm["github_number"])] = path
            except Exception:
                pass
                
        for issue_item in remote_issues:
            if "pull_request" in issue_item:
                continue
                
            number = issue_item.get("number")
            title = issue_item.get("title", "")
            state = issue_item.get("state", "open")
            html_url = issue_item.get("html_url", "")
            body = issue_item.get("body", "") or ""
            
            if number in local_issues:
                path = local_issues[number]
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    fm = parse_issue_frontmatter(content)
                    current_status = fm.get("status")
                    if current_status and current_status != state:
                        lines = content.split('\n')
                        in_fm = False
                        updated = False
                        for idx, line in enumerate(lines):
                            if line.strip() == '---':
                                if in_fm:
                                    break
                                in_fm = True
                                continue
                            if in_fm and line.strip().startswith('status:'):
                                lines[idx] = f"status: {state}"
                                updated = True
                        if updated:
                            content = '\n'.join(lines)
                            with open(path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            logger.success(f"Updated local issue #{number} status to '{state}'.")
                except Exception:
                    pass
            else:
                issue_id = f"issue-{number}"
                file_path = os.path.join(ISSUE_DIR, f"issue_{number}.md")
                current_date = datetime.now().strftime("%Y-%m-%d")
                
                title_escaped = title.replace('"', '\\"')
                template = f"""---
id: {issue_id}
title: "{title_escaped}"
status: {state}
assignee: agent-antigravity
created_at: {current_date}
github_url: "{html_url}"
github_number: {number}
---

# Issue Details

## Problem Statement
{body}

## Tasks
- [ ] Implement remote synchronization fixes <!-- id: sync-fixes -->

## Acceptance Criteria
- [ ] Verification complete
"""
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(template)
                    logger.success(f"Pulled new remote issue #{number} as local file '{file_path}'.")
                except Exception:
                    pass
    except Exception as e:
        logger.warn(f"Issue synchronization failed: {e}")
    finally:
        sync_board_with_issues()

def push_offline_issues():
    if not os.path.exists(ISSUE_DIR):
        return
        
    import git_api
    pat = git_api.get_pat()
    repo = git_api.get_repo_info()
    if not pat or not repo:
        return
        
    logger.info("Auditing local issues for offline creations...")
    for f_name in os.listdir(ISSUE_DIR):
        if not f_name.endswith(".md") or "example" in f_name:
            continue
        path = os.path.join(ISSUE_DIR, f_name)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            fm = parse_issue_frontmatter(content)
            github_number = fm.get("github_number")
            github_url = fm.get("github_url")
            issue_id = fm.get("id")
            title = fm.get("title")
            
            if not github_number and issue_id and title:
                logger.info(f"Pushing local issue '{issue_id}' to GitHub remote...")
                res = git_api.create_github_issue(title, f"Local tracking ID: {issue_id}")
                if res:
                    url, number = res
                    lines = content.splitlines()
                    boundary_indices = [idx for idx, line in enumerate(lines) if line.strip() == '---']
                    if len(boundary_indices) >= 2:
                        insert_idx = boundary_indices[1]
                        lines.insert(insert_idx, f"github_url: \"{url}\"")
                        lines.insert(insert_idx + 1, f"github_number: {number}")
                        new_content = "\n".join(lines) + "\n"
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        logger.success(f"Successfully linked local issue '{issue_id}' to remote GitHub issue #{number}.")
        except Exception as e:
            logger.warn(f"Failed to push local issue '{f_name}': {e}")

def get_issue_path(issue_id):
    normalized = issue_id.lower().replace('-', '_')
    if not os.path.exists(ISSUE_DIR):
        os.makedirs(ISSUE_DIR, exist_ok=True)
    for f in os.listdir(ISSUE_DIR):
        if normalized in f.lower().replace('-', '_') or issue_id.lower() in f.lower():
            return os.path.join(ISSUE_DIR, f)
    archive_dir = ".agents/archive/issues"
    if os.path.exists(archive_dir):
        try:
            for f in os.listdir(archive_dir):
                if normalized in f.lower().replace('-', '_') or issue_id.lower() in f.lower():
                    return os.path.join(archive_dir, f)
        except Exception:
            pass
    suffix = normalized
    if suffix.startswith("issue_"):
        suffix = suffix[6:]
    elif suffix.startswith("task_"):
        suffix = suffix[5:]
    return os.path.join(ISSUE_DIR, f"issue_{suffix}.md")
