import re
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

class ValidationError(ValueError):
    """Raised when domain entity validation fails."""
    pass

@dataclass
class GitProfile:
    name: str
    email: str
    signing_key: Optional[str] = None
    ssh_key_path: Optional[str] = None
    git_pat: Optional[str] = None
    github_mcp_pat: Optional[str] = None
    gitea_token: Optional[str] = None
    gitea_host: Optional[str] = None
    active: bool = False

    def validate(self) -> None:
        """Validate that structural invariants are maintained."""
        if not self.name.strip():
            raise ValidationError("Profile name cannot be empty.")
        if not re.match(r"^[a-zA-Z0-9_\-\.]+$", self.name):
            raise ValidationError(f"Invalid profile name format: '{self.name}'. Only alphanumeric, underscores, hyphens, and dots allowed.")
            
        if not self.email.strip() or "@" not in self.email or "." not in self.email:
            raise ValidationError(f"Invalid email format: '{self.email}'.")

        # Path injection check on keys if specified
        for path_field, path_val in (("ssh_key_path", self.ssh_key_path),):
            if path_val:
                if any(char in path_val for char in (";", "&&", "||", "|", "`", "$", "\n", "\r")):
                    raise ValidationError(f"Command injection detected in {path_field}: '{path_val}'.")

        if self.gitea_host:
            if not self.gitea_host.startswith(("http://", "https://")):
                raise ValidationError(f"Gitea host must start with http:// or https://, got: '{self.gitea_host}'.")
            if any(char in self.gitea_host for char in (";", "&&", "||", "|", "`", "$", "\n", "\r", " ")):
                raise ValidationError(f"Command injection/space characters detected in gitea_host: '{self.gitea_host}'.")

    @classmethod
    def from_dict(cls, data: dict) -> 'GitProfile':
        return cls(
            name=data.get("name", ""),
            email=data.get("email", ""),
            signing_key=data.get("signing_key"),
            ssh_key_path=data.get("ssh_key_path"),
            git_pat=data.get("git_pat"),
            github_mcp_pat=data.get("github_mcp_pat"),
            gitea_token=data.get("gitea_token"),
            gitea_host=data.get("gitea_host"),
            active=data.get("active", False)
        )

    def to_dict(self) -> dict:
        d = {
            "name": self.name,
            "email": self.email,
            "active": self.active
        }
        if self.signing_key is not None:
            d["signing_key"] = self.signing_key
        if self.ssh_key_path is not None:
            d["ssh_key_path"] = self.ssh_key_path
        if self.git_pat is not None:
            d["git_pat"] = self.git_pat
        if self.github_mcp_pat is not None:
            d["github_mcp_pat"] = self.github_mcp_pat
        if self.gitea_token is not None:
            d["gitea_token"] = self.gitea_token
        if self.gitea_host is not None:
            d["gitea_host"] = self.gitea_host
        return d

@dataclass
class ModuleLock:
    module: str
    branch: str

    def validate(self) -> None:
        """Validate path injection safety on both module and branch."""
        blacklist = [';', '&&', '||', '|', '`', '$(', '\n', '\r']
        if not self.module or any(c in self.module for c in blacklist):
            raise ValidationError(f"Invalid/unsafe module lock path: '{self.module}'.")
        if not self.branch or any(c in self.branch for c in blacklist):
            raise ValidationError(f"Invalid/unsafe lock branch: '{self.branch}'.")

    @classmethod
    def from_dict(cls, module: str, branch: str) -> 'ModuleLock':
        return cls(module=module, branch=branch)

@dataclass
class TokenBudget:
    account: str
    daily_limit: int = 500000
    daily_used: int = 0
    monthly_limit: int = 10000000
    monthly_used: int = 0
    last_reset: str = ""
    tasks: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    rolling_quotas: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Verify budget constraints are valid."""
        if self.daily_limit < 0 or self.daily_used < 0:
            raise ValidationError("Daily tokens values cannot be negative.")
        if self.monthly_limit < 0 or self.monthly_used < 0:
            raise ValidationError("Monthly tokens values cannot be negative.")

    @classmethod
    def from_dict(cls, account: str, data: dict) -> 'TokenBudget':
        return cls(
            account=account,
            daily_limit=data.get("daily_limit", 500000),
            daily_used=data.get("daily_used", 0),
            monthly_limit=data.get("monthly_limit", 10000000),
            monthly_used=data.get("monthly_used", 0),
            last_reset=data.get("last_reset", ""),
            tasks=data.get("tasks", {}),
            rolling_quotas=data.get("rolling_quotas", {})
        )

    def to_dict(self) -> dict:
        return {
            "daily_limit": self.daily_limit,
            "daily_used": self.daily_used,
            "monthly_limit": self.monthly_limit,
            "monthly_used": self.monthly_used,
            "last_reset": self.last_reset,
            "tasks": self.tasks,
            "rolling_quotas": self.rolling_quotas
        }

@dataclass
class Issue:
    id: str
    title: str
    status: str = "open"
    assignee: str = "agent-antigravity"
    created_at: str = ""
    github_url: Optional[str] = None
    github_number: Optional[int] = None

    def validate(self) -> None:
        """Validate issue format and safe status."""
        if not self.id:
            raise ValidationError("Issue ID cannot be empty.")
        if not re.match(r"^[a-zA-Z0-9_\-\.]+$", self.id):
            raise ValidationError(f"Invalid Issue ID format: '{self.id}'. Only alphanumeric, underscores, hyphens, and dots allowed.")

        allowed_status = {"open", "doing", "closed", "done"}
        if self.status.lower() not in allowed_status:
            raise ValidationError(f"Invalid status value: '{self.status}'. Must be one of {allowed_status}.")

    @classmethod
    def from_dict(cls, data: dict) -> 'Issue':
        github_num = data.get("github_number")
        if github_num is not None:
            try:
                github_num = int(github_num)
            except ValueError:
                pass
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            status=data.get("status", "open"),
            assignee=data.get("assignee", "agent-antigravity"),
            created_at=data.get("created_at", ""),
            github_url=data.get("github_url"),
            github_number=github_num
        )

    def to_dict(self) -> dict:
        d = {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "assignee": self.assignee,
            "created_at": self.created_at
        }
        if self.github_url is not None:
            d["github_url"] = self.github_url
        if self.github_number is not None:
            d["github_number"] = self.github_number
        return d
