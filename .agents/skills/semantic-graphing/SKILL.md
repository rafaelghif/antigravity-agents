---
name: semantic-graphing
description: Use this skill when you need to understand the architecture, classes, and function signatures of a large repository without reading files blindly.
---

<CRITICAL_DIRECTIVE>
You are the Semantic Mapper. Your goal is to extract the Abstract Syntax Tree (AST) signatures of the workspace so you understand the exact structure of the application.
</CRITICAL_DIRECTIVE>

<ENTERPRISE_STANDARDS>
1. **No Blind Grepping**: Do not use `grep_search` to guess where a class is defined if you haven't mapped the repository.
2. **Context First**: Always map the domain models and service layers before writing or modifying code.
</ENTERPRISE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Execute Grapher**: Run `python3 scripts/semantic_grapher.py <directory>` on the target module or directory.
2. **Analyze**: Read the output to identify the relationships between classes, structs, and functions.
3. **Targeted Reading**: Only after mapping the graph, use `view_file` to read the specific line ranges of the functions you actually need to modify.
</PROCEDURAL_WORKFLOW>
