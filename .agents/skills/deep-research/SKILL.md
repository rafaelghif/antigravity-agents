---
name: deep-research
description: Use this skill when researching unfamiliar libraries, looking up official documentation, verifying external API contracts, or investigating unfamiliar errors.
license: Apache-2.0
compatibility: posix, windows, python3
metadata:
  author: AAC Antigravity
  version: "4.47.0"
  category: research
  tags: [deep-research, documentation, grounding, anti-hallucination]
---

# Deep Research & External Grounding Protocol

**Role**: Principal Technical Researcher & Epistemic Grounding Specialist.

## Overview & Trigger Conditions
Activate this skill when encountering unfamiliar libraries, framework migrations, external APIs, deprecation notices, or complex system errors. Agents MUST NEVER guess, hallucinate, or assume method signatures, configuration keys, or interface types.

**Trigger Scenarios & Keywords**:
- External API lookups, framework documentation, SDK migration guides, RFC references.
- Keywords: `research`, `search web`, `browse`, `documentation`, `docs`, `lookup`, `rfc`, `investigate`, `latest version`, `official guide`, `api reference`.

## Core Standards & Invariants

1. **Anti-Hallucination Baseline**:
   - Zero invention: never guess non-existent function arguments, CLI flags, package exports, or configuration properties.
   - If an API or feature cannot be confirmed via official documentation or local code inspection, explicitly label it `UNKNOWN / UNVERIFIED`.

2. **Official Source Hierarchy**:
   - **Tier 1 (Authoritative)**: Official language and package documentation (`docs.python.org`, `pkg.go.dev`, `developer.mozilla.org`, `crates.io`, `docs.rs`).
   - **Tier 2 (Vendor & Standards)**: Official vendor documentation, RFC specifications, GitHub release notes, and library migration guides.
   - **Tier 3 (Secondary)**: Community forums and blog posts (must always be verified against Tier 1/2 official documentation).

3. **Reconciliation with Local Codebase (`scripts/grounding.py`)**:
   - Always cross-reference external documentation with the actual installed versions in the repository (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`).
   - Never adopt newer syntax or APIs that are incompatible with the repository's pinned dependencies or runtime versions.

## The 3-Step External Grounding Loop

1. **Targeted Web Search (`search_web`)**:
   - Formulate precise, high-density queries including language, library version, and exact error/method name:
     - Good: `"pydantic v2 model_validate JSON schema migration guide"`
     - Bad: `"how to fix python error"`

2. **Deep Content Extraction (`read_url_content`)**:
   - Fetch the markdown documentation from the top official URL. Extract method signatures, parameter types, return values, and deprecations.

3. **Local Synthesis & Validation**:
   - Compare extracted API contracts with local repository patterns.
   - Run `python3 scripts/grounding.py` to confirm target ecosystem compatibility.

## Golden Example: Research Evidence Citation
When recording research findings, format as an epistemic evidence citation:
```markdown
- **Source**: https://docs.pydantic.dev/2.8/migration/
- **Verified Signature**: `BaseModel.model_validate(obj, *, strict=None, from_attributes=None, context=None)`
- **Local Compatibility**: Confirmed via `pyproject.toml` (pydantic >= 2.6.0). Replaces deprecated `parse_obj()`.
```

## Procedural Workflow
1. **Identify Unknown**: Isolate ambiguous API, type, or library error.
2. **Execute Search**: Run `search_web` targeting Tier 1/2 official domains.
3. **Extract & Ground**: Call `read_url_content` and reconcile with `python3 scripts/grounding.py`.
4. **Implement**: Apply verified method signatures and error contracts.
5. **Verify**: Run `python3 scripts/verify.py --execute --terse`.

## Anti-Patterns & Common Pitfalls
- **Hallucinated Methods**: Calling imaginary methods invented by LLMs without checking official docs.
- **Version Mismatch**: Using API patterns from modern versions (Next.js App Router) in a project pinned to legacy versions (Pages Router).
- **Unverified Third-Party Code**: Copying StackOverflow snippets containing obsolete security practices.
