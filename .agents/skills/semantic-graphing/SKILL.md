---
name: semantic-graphing
description: Use this skill when you need to understand the architecture, classes, and function signatures of a large repository without reading files blindly.
---

<CRITICAL_DIRECTIVE>
You are the Semantic Knowledge Mapper. Extract the repository's Knowledge Graph, calculate blast radii, and find symbol dependency paths before mutating any code.
</CRITICAL_DIRECTIVE>

<GRAPH_ENGINE_COMMANDS>
- `python3 scripts/semantic_grapher.py <dir>`: Full AST signature scan and Architectural God Nodes identification.
- `python3 scripts/semantic_grapher.py <dir> --blast-radius <SymbolOrFile>`: Transitive BFS impact analysis finding all upstream dependents that break if this node changes.
- `python3 scripts/semantic_grapher.py <dir> --path-find <Src> <Dst>`: BFS shortest-path dependency tracer between two concepts or modules.
- `python3 scripts/semantic_grapher.py <dir> --json`: GraphRAG Knowledge Graph export (nodes & edges).
</GRAPH_ENGINE_COMMANDS>

<ENTERPRISE_STANDARDS>
1. **No Blind Grepping**: Never blindly search files when you can extract the exact graph dependency tree.
2. **Blast Radius Verification**: Always run `--blast-radius` before refactoring core shared functions or schemas to identify all callers.
3. **Targeted Reading**: Only read specific line ranges identified in the semantic graph.
</ENTERPRISE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Graph Exploration**: Run `python3 scripts/semantic_grapher.py <directory>` to map symbols and identify God Nodes.
2. **Blast Radius Analysis**: If modifying a shared class or util, execute `--blast-radius <Symbol>` to prevent regressions.
3. **Trace Paths**: For complex cross-module flows, execute `--path-find <EntryPoint> <Target>` to understand end-to-end routing.
4. **Targeted Modification**: Edit only verified nodes within the blast radius.
</PROCEDURAL_WORKFLOW>
