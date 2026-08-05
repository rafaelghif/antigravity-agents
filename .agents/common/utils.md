# Shared Procedures

Use only when a task needs them:

- **Retry**: retry transient network failures up to `config.json` limits; never retry deterministic failures.
- **Redaction**: redact bearer tokens, API keys, private keys, and credential URLs before logs.
- **Locking**: use an atomic lock only for concurrent plan/state mutation; do not claim a lock for ordinary single-agent edits.
- **Recovery**: prefer Git history and tracked plans; remove stale local backups after delivery.
- **Verification**: call `python3 scripts/verify.py`, then run the detected project checks it reports.
