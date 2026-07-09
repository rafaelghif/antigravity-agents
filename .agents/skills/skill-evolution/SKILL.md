---
name: skill-evolution
description: Playbook instructing agents how to dynamically formulate, design, bootstrap, and register new workspace skills when facing skill gaps.
---

# Skill Evolution & Dynamic Bootstrapping Playbook

This playbook defines the standardized operational protocol for autonomous agents to dynamically extend their capabilities by creating, scaffolding, and registering new skills within the workspace when encountering domain-specific tasks that are not covered by existing playbooks.

---

## 1. When to Create a New Skill

An agent must proactively bootstrap a new skill under `.agents/skills/` if ANY of the following conditions are met:
1. **Tooling Integration:** A new test framework, linter, database migration tool, or external CLI is introduced and needs standard operational playbooks.
2. **Domain Specialization:** A task requires domain-specific instructions (e.g., frontend styling systems, security hardening guidelines, custom script execution flows) not detailed in the 14 baseline skills.
3. **Task Repetition:** An implementation workflow requires multi-step procedures that will be reused by future agents or in subtasks.
4. **Architectural Divergence:** The codebase adopts new frameworks or API contracts requiring specialized validation rules.

---

## 2. Bootstrapping Protocol (Step-by-Step)

When a skill gap is identified, the agent must perform the following atomic steps:

### Step 1: Design the Skill Scope & Architecture
Before creating any files, perform a Pre-Implementation Impact Analysis comparing the new skill structure with existing skills to avoid duplicate guidelines. Keep the name lowercase and kebab-cased (e.g., `frontend-standards`).

### Step 2: Scaffold Directory & Playbook File
Create the subdirectory under `.agents/skills/<skill-name>/` and create the `SKILL.md` file. The file MUST include standard YAML frontmatter:
```yaml
---
name: <skill-name>
description: <Short, precise 1-2 sentence description of when to use this skill.>
---
```

### Step 3: Write Detailed Playbooks & References
Write structured markdown guidelines including:
* **Context & Core Principles:** Core standards and reasoning rules for the domain.
* **Commands Reference:** Code snippets and console commands to execute the work.
* **Best Practices & Gaps:** Common pitfalls, safety warnings, and how to verify correctness.
* **Optionally:** Add helper scripts under a `scripts/` folder or examples under an `examples/` folder if the playbook requires automated actions.

### Step 4: Register & Synchronize the Workspace Skill
Always run the sync CLI command to index the new skill inside `AGENTS.md` and rebuild context manifests:
```bash
./helper.sh sync
```

---

## 3. Playbook Scaffolding Template

Use the following markdown template when creating `SKILL.md`:

```markdown
---
name: skill-name-here
description: Concise description of the skill and when it matches.
---

# Skill Title Here

Background context on this skill domain and why it is active.

## 1. Core Principles
* Rule 1
* Rule 2

## 2. Operational CLI Commands
```bash
# Provide exact command lines
./helper.sh command-here
```

## 3. Implementation Checklist & Verification
* [ ] Check 1
* [ ] Verify 2
```
