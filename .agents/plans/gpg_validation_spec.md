# Pre-Implementation Impact Analysis

## Issue ID: issue-037
## Title: Validate GPG signing key validity during profile switch

This analysis compares the chosen design options for this task.

---

### Option A: Local GPG Keyring Validation (Recommended)
Before switching profiles, if the target profile has a `signing_key` and it's not a placeholder (e.g. doesn't end with `...`), we execute:
`gpg --list-secret-keys --keyid-format LONG <signing_key>`

If the command fails (return code != 0), it indicates that the key is missing or invalid in the developer's GPG setup. We prevent switching and print an error message, unless `--force-no-gpg` is supplied.

#### Pros:
- Catches configuration issues early before Git commits fail.
- Provides a clear bypass option for automated or special testing environments.

#### Cons:
- Depends on `gpg` command availability. We should gracefully handle environments where `gpg` is not installed or when mock-testing.

---

### Option B: Check regex formatting only
Verify that the signing key matches hexadecimal format.

#### Pros:
- Simple, no dependency on external binary `gpg`.

#### Cons:
- Doesn't verify if the GPG key is actually installed on the machine, meaning signed commits could still fail later.

---

### Recommendation
**Option A** is the recommended choice because it validates the actual usability of the GPG key on the system.
