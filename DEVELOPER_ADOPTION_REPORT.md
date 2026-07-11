# Developer Adoption & Experience Report
**Project:** Antigravity Agent Core (AAC) V3  

---

This report evaluates the **Developer Experience (DX)** of the Antigravity Agent Core (AAC) V3, highlighting barriers to developer adoption, usability concerns, documentation quality, and recommendations for maximizing project trust and maintainability.

---

## 1. Onboarding Friction

The onboarding process is structured around two main entry scripts: `install.sh` / `install.ps1` and `bootstrap.sh` / `bootstrap.ps1`. 

### Friction Points:
- **Environment Prerequisites**: A developer must have Python 3.8+ and Git pre-installed. While standard on developer machines, this represents a setup step that is not automated by the installers.
- **Interactive Prompts vs. Headless CI**: The bootstrap script prompts the user for project configurations (project name, stack, architecture type). If run inside headless or non-interactive environments, this could pause or fail if the quick-setup options are not explicitly configured.
- **SSH and GPG Configuration**: During setup, the bootstrapper tries to resolve GPG keys and SSH keys. For junior developers, configurating corporate GPG signing profiles can be a major friction point.

---

## 2. Usability & Command Discoverability

The command-line interface provides high usability:
- The global launcher setup (`helper.sh install-global`) creates a global `aac` shell command, making CLI tools accessible from any directory.
- Features like shell autocomplete (`helper.sh completion`) significantly enhance CLI usability.
- **Usability Gap**: If a developer makes a typo in their branch name (e.g., using `feature/297` instead of `feat/issue-297`), the validation guard blocks commits immediately, forcing the developer to research branch renaming commands or bypass hook files.

---

## 3. Trust & Reliability

Developers will trust the framework due to:
- **Zero-Dependency Footprint**: Installing the agent manager does not clutter system Python package lists.
- **Sandboxed Validations**: The validation tool copies files to a temporary virtual sandbox before executing tests. Developers can rest assured that validation scripts will not modify active workspace files.
- **Git Safety Guard**: Excludes destructive git commands (such as hard resets or force pushes), giving developers confidence that their work tree will not be cleaned.

---

## 4. Documentation Quality

Documentation files are comprehensive:
- `README.md` outlines CLI commands, monorepos setup, and profile configuration.
- `AGENTS.md` and `.agents/rules.md` detail instructions for agent collaboration.
- `context_map.md` serves as a solid directory sitemap.
- **Documentation Gaps**: Lacks concrete examples of configuring the CLI for complex team environments. Lacks a clear troubleshooting section for resolving locked modules or broken hook installations.

---

## 5. Long-Term Adoption Risks

If not addressed, developers may stop using the tool due to:
- **Strict Validation Fatigue**: The validation guard enforces multiple criteria (branch naming, lock compliance, commit format). If developers feel the tool blocks their workflow for trivial format changes, they may disable the Git commit hooks.
- **Platform Drift Overhead**: If wrappers on Bash and PowerShell deviate, developers working on different systems (e.g. Windows vs Linux) will get inconsistent setup behaviors.
- **Credential Storage Security**: Storing raw PAT tokens inside JSON config files is a compliance violation for enterprise organizations, which could block corporate adoption.

---

## 6. Recommendations to Maximize Adoption

1. **Provide Auto-Repair Options**: Instead of hard-failing validations on branch naming typos, offer to automatically rename the branch to the correct convention.
2. **Support Secure Key Vaults**: Integrate credential retrieval from secure system keychains or environment variables rather than persisting plain-text tokens in configuration files.
3. **Establish a Diagnostics "Self-Heal" Option**: Extend the `helper.sh doctor` command to automatically repair broken permissions or clean stale lock files without manual developer configuration.
