---
name: conversational-agent
description: Playbook for translating natural language requests about tasks, profiles, locking, and validation into CLI helper executions.
---

# Conversational Agent Playbook

When the user asks to switch profiles, manage tasks, lock modules, or audit code in natural language:

## 1. Profile Rotation & Matching
- User says: *"Switch to my home email"* or *"Switch to corp profile"*
- Action: Call the `run_command` tool with:
  ```bash
  ./helper.sh profile switch <profile-name>
  ```
  *(If the profile name is not specified, run `./helper.sh profile list` first to show available profiles.)*

## 2. Lock Management
- User says: *"Lock validate"* or *"Unlock git_api"*
- Action:
  * For locking: `./helper.sh lock <module-name>`
  * For unlocking: `./helper.sh lock <module-name> --release`

## 3. Issue and Task Tracking
- User says: *"Create task for web UI"* or *"Mark issue-123 as complete"*
- Action:
  * For creating issues: `./helper.sh issue create <id> "<title>"`
  * For closing issues: `./helper.sh issue close <id>`
  * For listing tasks: `./helper.sh issue list`

## 4. Run Audits & Checks
- User says: *"Check my workspace health"* or *"Validate project before commit"*
- Action:
  * For general diagnostics: `./helper.sh doctor`
  * For validation audits: `./helper.sh validate`
