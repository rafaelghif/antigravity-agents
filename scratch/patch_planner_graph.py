import re
from pathlib import Path

# Update planner to use semantic grapher for refactoring
planner = Path('.agents/agents/planner.md')
p_content = planner.read_text(encoding='utf-8')
p_content = re.sub(
    r'2\. \*\*Reconnaissance\*\*: Read the required files, dependencies, and adjacent test suites\.',
    r'2. **Reconnaissance**: For multi-file changes or refactors, you MUST first run `python3 scripts/semantic_grapher.py` to get an AST map of the codebase. Use this X-Ray map to identify exact interconnected files before running `view_file` on them.',
    p_content
)
planner.write_text(p_content, encoding='utf-8')

# Update reviewer to use semantic grapher for impact analysis
reviewer = Path('.agents/agents/reviewer.md')
r_content = reviewer.read_text(encoding='utf-8')
r_content = re.sub(
    r'2\. \*\*Diff Inspection\*\*: Review the exact diff\. Check for logic errors, missing edge-case tests, or violations of code-quality constraints',
    r'2. **Diff Inspection & Impact Analysis**: Review the exact diff. If reviewing a refactor, run `scripts/semantic_grapher.py` to verify that no interconnected functions/classes were missed. Check for logic errors, edge-cases, and Big-O constraints',
    r_content
)
reviewer.write_text(r_content, encoding='utf-8')
