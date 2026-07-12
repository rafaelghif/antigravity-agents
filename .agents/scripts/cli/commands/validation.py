import re

def validate_safe_path(path: str) -> bool:
    """Validate that the path does not contain shell command injection characters."""
    if not path:
        return False
    # Permit alphanumeric, dots, hyphens, underscores, slashes, backslashes, colons, tildes, and spaces.
    # Block characters like ;, &&, |, `, $, etc.
    pattern = r"^[a-zA-Z0-9_\-\.\/\~\:\s\\]+$"
    if not re.match(pattern, path):
        return False
    # Extra check for common injection patterns
    blacklist = [';', '&&', '||', '|', '`', '$(', '\n', '\r']
    return not any(char in path for char in blacklist)

def validate_safe_identifier(name: str) -> bool:
    """Validate that the identifier (profile name, issue ID, skill name) is safe and does not contain shell injects."""
    if not name:
        return False
    # Only alphanumeric, hyphens, underscores, and dots (e.g. issues could be issue-123 or task-abc)
    pattern = r"^[a-zA-Z0-9_\-\.]+$"
    return bool(re.match(pattern, name))

def validate_safe_branch(branch: str) -> bool:
    """Validate that the branch name does not contain shell injection characters."""
    if not branch:
        return False
    # Permit only alphanumeric, slashes, hyphens, and underscores (standard git branch characters)
    pattern = r"^[a-zA-Z0-9_\-\/]+$"
    return bool(re.match(pattern, branch))
