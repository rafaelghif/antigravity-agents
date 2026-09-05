---
name: semantic-graphing
description: Use this skill when exploring codebase architecture, calculating blast radii of refactors, mapping symbol dependencies, or identifying central hub nodes without reading files blindly.
license: Apache-2.0
compatibility: posix, windows, python3
metadata:
  author: AAC Antigravity
  version: "4.47.0"
  category: code-intelligence
  tags: [ast, blast-radius, pagerank, call-graph, dependencies]
---

# Semantic Codebase Graphing & Blast Radius Protocol

**Role**: Principal Code Intelligence & AST Architecture Specialist.

## Overview & Trigger Conditions
Activate this skill when exploring new codebases, planning non-trivial refactors, identifying high-risk Architectural God Nodes, mapping symbol caller graphs, or evaluating the blast radius of API/schema modifications.

**Trigger Scenarios & Keywords**:
- Codebase reconnaissance, blast radius calculation, caller dependency trees, God Node identification, AST symbol scanning.
- Keywords: `semantic graph`, `knowledge graph`, `blast radius`, `call graph`, `dependency tree`, `ast scan`, `pagerank`.

## Core Standards & Invariants

1. **Epistemic Exploration over Blind Grepping**:
   - Never blindly inspect large files or dump directories when understanding architecture.
   - Extract the AST symbol dependency graph to identify module boundaries, central hubs, and interface contracts.

2. **Mandatory Blast Radius Calculation**:
   - Before modifying or deprecating any shared function, utility, base class, or model, calculate the transitive blast radius:
     Identify ALL upstream callers that could break.
   - Refactorings with a large blast radius (> 10 dependent files) require an Architecture Decision Record (ADR) and phased rollout.

3. **Architectural God Node & Hub Awareness**:
   - Use PageRank centrality to identify core system hubs.
   - High-centrality hub nodes require strict backward compatibility, zero breaking changes, and 100% test coverage.

4. **Targeted Reading & Context Economy**:
   - Only read the specific line ranges identified in the semantic graph using `view_file` slice notation (`StartLine` / `EndLine`). Avoid reading irrelevant lines.

## Graph Engine Commands (`scripts/semantic_grapher.py`)

- **Full Codebase AST Scan & Hub Identification**:
  `python3 scripts/semantic_grapher.py <dir>`
- **Transitive Blast Radius Resolution**:
  `python3 scripts/semantic_grapher.py <dir> --blast-radius <Symbol>`
  *Performs transitive BFS to detect all direct and indirect upstream dependents of a symbol.*
- **PageRank Centrality Ranking**:
  `python3 scripts/semantic_grapher.py <dir> --pagerank --top-central 10`
  *Ranks top 10 architectural hub symbols in the repository.*
- **BFS Shortest-Path Dependency Tracer**:
  `python3 scripts/semantic_grapher.py <dir> --path-find <StartSymbol> <EndSymbol>`
  *Traces end-to-end invocation flow between two disparate components.*
- **GraphRAG Knowledge Graph Export**:
  `python3 scripts/semantic_grapher.py <dir> --json`
  *Exports structured JSON graph (nodes and edges) for ingestion.*

## Golden Example: Graph Exploration Workflow
```bash
# 1. Identify Central God Nodes (PageRank)
python3 scripts/semantic_grapher.py . --pagerank --top-central 5

# 2. Resolve Blast Radius before modifying target function
python3 scripts/semantic_grapher.py . --blast-radius ground_workspace
```

## Procedural Workflow
1. **Map Layout**: Run `python3 scripts/semantic_grapher.py .` to scan the project AST.
2. **Rank Centrality**: Run `--pagerank --top-central 10` to understand architectural hubs.
3. **Trace Blast Radius**: Run `--blast-radius <Symbol>` before touching shared code.
4. **Targeted Inspection & Edit**: Inspect only affected callers and apply focused modifications.
5. **Local Verification**: Run `python3 scripts/verify.py --execute --terse`.

## Anti-Patterns & Common Pitfalls
- **Blind Multi-File Search-and-Replace**: Using regex find-and-replace across a codebase without verifying AST node contexts and transitive callers.
- **Ignoring Hub Dependencies**: Mutating a high-PageRank God Node without regression testing downstream dependents.
