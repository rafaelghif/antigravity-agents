# Pre-Implementation Impact Analysis: Auto-Lessons Extractor on Issue Close

We evaluate two options to implement the auto-lessons extractor when closing an issue.

## Option A: Direct Inline Interactive Questionnaire
Directly prompt the user with a generic "What did you learn?" question when closing the issue, without parsing the git diff.
- **Pros**: Extremely simple to implement. Zero risk of Git parsing bugs.
- **Cons**: Fails the requirement of automatically analyzing the Git diff summary (e.g., detecting mock testing fixes, schema modifications, or path handling bugs) and suggesting tailored lessons learned. High cognitive load for the developer.

## Option B: Diff-Driven Heuristic Analyzer & Interactive Prompt (Recommended)
Automatically run `git diff` on the feature branch compared to the base branch, scan the diff files/lines for specific key concepts (e.g., `mock`, `schema`, `path`), auto-generate suggested lessons learned complete with relevant categories, and display an interactive menu to the user. The user can select a suggestion, type a custom lesson, or skip.
- **Pros**: Fulfills the requirement 100%. Provides a high-quality Developer Experience (DX) by auto-suggesting categories and draft lessons based on the actual changes.
- **Cons**: Slightly higher code complexity. Requires robust Git diff execution and pattern matching.

### Downstream Impacts
- Modifies the CLI issue close workflow in `.agents/scripts/cli/commands/issue.py` by adding an interactive step.
- Updates `.agents/memory/lessons-learned.yaml`.
- Requires modifying the test suite to mock interactive inputs (`sys.stdin`) and command line diff outputs.

**Decision**: **Option B** is selected because it fully satisfies the requirements, automates context extraction, and provides a polished interactive experience.
