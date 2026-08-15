# Shared Procedures

Use only when a task needs them:

- **Retry**: restrict retries exclusively to transient network failures up to `config.json` limits.
- **Redaction**: redact bearer tokens, API keys, private keys, and credential URLs before logs.
- **Locking**: restrict atomic locks exclusively to concurrent plan/state mutation.
- **Recovery**: prefer Git history and tracked plans; remove stale local backups after delivery.
- **Verification**: call `python3 scripts/verify.py`, then run the detected project checks it reports.
