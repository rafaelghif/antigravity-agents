---
name: security-rules
activation: Always On


---

# security-rules Workspace Rule

## Guidelines
- **Required Configuration Variables**:
  - `PORT` -> Server port configuration
  - `DATABASE_URL` -> Database connection connection string
  - `JWT_SECRET` -> Token encryption secret key
- **Environment Access Insulation**:
  - Never access `process.env` directly outside of a central configuration module/adapter (e.g. `src/config/index.ts`). All application components must import parameters from this config module to avoid scattered environment variables and maintain domain purity.
- **Credentials Scanner**:
  - Avoid committing passwords, private keys, API secrets, or certificates. Ensure all secrets are injected at runtime via environment variables.
