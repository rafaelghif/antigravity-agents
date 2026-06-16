# Task Workflow: Migrate README to Modular Documentation

This task migrates the detailed sections of `README.md` into modular documentation files under `.agents/docs/` to make the root directory clean. It also links the main `README.md` to the detailed docs, `CHANGELOG.md`, etc.

## 1. Scope of Work & Rationale
- **High-level README**: Re-architect `README.md` to serve as a concise, premium landing page, containing a quick feature overview, disclaimer, 30-second quick start, and a table of contents linking directly to the new sub-documents under `.agents/docs/`.
- **Modular Docs Creation**:
  - `directory_blueprint.md` -> Section 1: Directory Structure Blueprint
  - `features_capabilities.md` -> Section 2: Core Features & Capabilities
  - `setup_guide.md` -> Section 3: Step-by-Step Setup Guide
  - `cli_guide.md` -> Section 4: Operational Scripts Guide (`helper.sh`)
  - `agent_workflow.md` -> Section 5: Typical Workflow for the Agent
  - `rules_architecture.md` -> Section 6: Core Rules & Architecture Purity
  - `migration_guide.md` -> Section 7: Migration Guide
- **Index Link Mapping**: Ensure all files inside `.agents/docs/` are cross-referenced with markdown links in the root `README.md` and `AGENTS.md`.

## 2. Checklist & Implementation Status

- [x] **Scaffold Documentation Files**
  - [x] Create `.agents/docs/directory_blueprint.md`
  - [x] Create `.agents/docs/features_capabilities.md`
  - [x] Create `.agents/docs/setup_guide.md`
  - [x] Create `.agents/docs/cli_guide.md`
  - [x] Create `.agents/docs/agent_workflow.md`
  - [x] Create `.agents/docs/rules_architecture.md`
  - [x] Create `.agents/docs/migration_guide.md`
- [x] **Revise README.md & Links**
  - [x] Rewrite `README.md` into a clean, modular format with links to the doc files, `CHANGELOG.md`, etc.
  - [x] Verify all file links (`file://...`) resolve correctly and are clickable in standard markdown readers.
- [x] **Verification & Validation**
  - [x] Run `./.agents/scripts/helper.sh validate` to verify workspace compliance
  - [x] Commit changes via helper script
