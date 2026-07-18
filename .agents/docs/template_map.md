# AAC V3 Template & Command Parity Map

This map defines the relationship between template configurations and their generated target files, as well as the platform parity required between wrapper scripts. 

Always check and update these relationships to prevent configuration-drift or platform-drift.

---

## 1. Template-to-Target File Mappings

Whenever any of the following target files are modified, their source template under `.agents/templates/` **MUST** be updated to match the changes.

| Source Template | Target Workspace File | Description |
| :--- | :--- | :--- |
| `.agents/templates/rules.md.template` | `.agents/rules.md` | Workspace rule declarations. |
| `.agents/templates/AGENTS.md.template` | `AGENTS.md` | Agent system prompt prepended template configuration. |
| `.agents/templates/config.json.template` | `.agents/config.json` | Advanced workspace-level runtime and workflow settings (e.g. solo mode). |
| `.agents/templates/mcp_config.json.template` | `.agents/mcp_config.json` | Model Context Protocol servers configuration. |
| `.agents/templates/schema.md.template` | `.agents/schema.md` | Master architecture & database blueprint. |
| `.agents/templates/gitignore.template` | `.gitignore` | Git version control exclusions. |
| `.agents/templates/antigravityignore.template` | `.antigravityignore` | Agent workspace parsing exclusions. |
| `.agents/templates/ci_github_workflow.yml.template` | `.github/workflows/verify.yml` | GitHub actions CI/CD definition. |
| `.agents/git_profiles.example` | `.agents/git_profiles.json` | Local Git profiles rotation configuration. |
| `.agents/projects.example` | `.agents/projects.json` | Local monorepo project configurations. |
| `.agents/templates/node_package.json.template` | `package.json` | Default Node project initializer package manifest. |
| `.agents/templates/php_composer.json.template` | `composer.json` | Default PHP project initializer composer manifest. |
| `.agents/templates/python_requirements.txt.template` | `requirements.txt` | Default Python project initializer requirements list. |
| `.agents/memory/templates/security-policy.md.template` | `.agents/memory/security-policy.md` | Security runbook and guidelines config. |
| `.agents/memory/templates/milestones.md.template` | `.agents/memory/milestones.md` | High-level roadmap and release tracker. |
| `.agents/memory/templates/architecture.md.template` | `.agents/memory/architecture.md` | Compressed system architecture summary. |
| `.agents/memory/templates/glossary.md.template` | `.agents/memory/glossary.md` | Core terminology index. |
| `.agents/memory/templates/tech-debt.md.template` | `.agents/memory/tech-debt.md` | Tech debt and known issues registry. |

---

## 2. Command Script Platform Parity

To ensure seamless execution on both Linux/macOS and Windows platforms, the shell wrappers **MUST** maintain exact functional parity. 

Whenever any command, command argument, flag, or option is added/modified on one script, the corresponding script on the other platform **MUST** be synchronized.

* **Helper Commands**: `helper.sh` (Bash) <--> `helper.ps1` (PowerShell)
* **Bootstrap Wrappers**: `bootstrap.sh` (Bash) <--> `bootstrap.ps1` (PowerShell)
* **Installer Wrappers**: `install.sh` (Bash) <--> `install.ps1` (PowerShell)

---

## 3. Operational Policy for Autonomous Agents

1. **Pre-flight Check**: Before saving edits to a config or shell script, look up this map to determine if a template or a twin platform script also requires updates.
2. **Synchronization**: Always execute `./helper.sh sync` after making template updates to rebuild registries and rule catalogs cleanly.
