---
id: issue-075
title: "Implement Automated SSH Key Generation for Developer Profiles"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
Implement Automated SSH Key Generation for Developer Profiles

## Tasks
- [x] Task 1: Create find_ssh_keygen and generate_ssh_key helper functions in profile.py.
- [x] Task 2: Implement --generate-ssh flag parsing and mutual exclusivity check in profile add CLI.
- [x] Task 3: Implement comprehensive unit tests.

## Acceptance Criteria
- [x] profile add command generates ed25519 SSH keys and sets ssh_key_path dynamically.
- [x] Wizard outputs the generated public key to console.
