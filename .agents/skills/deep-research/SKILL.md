---
name: deep-research
description: Epistemic web research, documentation lookup, and external API verification to eliminate hallucinations.
---

# Deep Research & External Grounding Skill

## Overview
When encountering unfamiliar libraries, framework migrations, external APIs, or complex errors, agents MUST NEVER guess or assume method signatures. This skill mandates systematic external verification using `search_web` and `read_url_content`.

## Protocol: The 3-Step External Grounding Loop

### 1. Targeted Web Search (`search_web`)
- Formulate precise, high-density queries including language, library version, and exact error/method name:
  - Good: `"pydantic v2 model_validate JSON schema migration guide"`
  - Good: `"golang net/http Timeout Handler context cancellation best practice"`
  - Bad: `"how to fix python error"`
- Prioritize official documentation domains (e.g. `docs.python.org`, `pkg.go.dev`, `crates.io`, `developer.mozilla.org`, `spring.io`).

### 2. Deep Content Extraction (`read_url_content`)
- Fetch the exact markdown documentation from the top official URL.
- Extract:
  - Exact function/method signatures, parameter types, and return values.
  - Required imports and package namespace.
  - Minimum supported version or deprecation warnings.

### 3. Synthesis with Local Codebase (`grounding.py`)
- Cross-reference retrieved documentation with local `scripts/grounding.py` output.
- Verify that the documented version matches what is actually installed in the workspace (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.).
- Never introduce breaking changes or incompatible newer API methods without checking local dependencies.

## Decision Matrix
| Situation | Action |
| :--- | :--- |
| Method signature unsure | Run `search_web` for official API reference |
| Third-party library error | Search exact error message + library version |
| Designing new architecture | Research RFCs, standard patterns, and security best practices |
| Local dependency missing | Check `grounding.py`; verify if installed before writing code |
