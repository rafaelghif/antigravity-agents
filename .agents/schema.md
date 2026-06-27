# AAC V2 Configuration Schemas

This schema documentation defines the models and JSON file formats used by the Antigravity Agent Core V2 system.

## 1. Token Budget Schema (`token_budget.json`)
Tracks API usage tokens and enforces budget limits.
```json
{
  "monthly_limit": 5000000,
  "monthly_used": 120000,
  "daily_limit": 500000,
  "daily_used": 15000,
  "last_reset": "2026-06-27T00:00:00Z"
}
```

## 2. Git Profile Schema (`git_profiles.json`)
Defines the rotation profiles for local commits.
```json
{
  "profiles": [
    {
      "name": "default",
      "email": "developer@example.com",
      "signing_key": "ssh-ed25519 AAAAC3...",
      "active": true
    }
  ]
}
```

## 3. Workspace State Schema (`memory.md` / `state.json`)
Maintains session locks and branch states.
- **branch**: Name of the active feature branch.
- **task_id**: Current active task ID from the board.
- **locks**: List of acquired module locks.
