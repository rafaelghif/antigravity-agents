# Sync Memory Workflow (/sync-memory)

This workflow command synchronizes session logs, task board updates, and architectural learnings into the project memory ledger.

## Execution Steps
1. **Commit Active ADRs**: Validate that any new architectural design decisions are compiled and saved in `.agents/memory/decisions/`.
2. **Audit Task Board**: Check that all checklist items in `.agents/tasks/board.md` match the actual repository branch status.
3. **Consolidate Lessons Learned**: Copy session learnings into `.agents/memory/lessons-learned.yaml`.
4. **Stage Changes**: Run `git add .agents/` to stage all memory updates.
