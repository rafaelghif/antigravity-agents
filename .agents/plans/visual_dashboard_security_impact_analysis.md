# Pre-Implementation Impact Analysis: Visual Dashboard Security (Issue-237)

## 1. Option Comparison Matrix

| Criteria | Option A: Transient CLI Token in URL (Recommended) | Option B: Local State Session File |
| --- | --- | --- |
| **Description** | Generate a cryptographically secure token on CLI startup, inject it as a query parameter in the launch URL, and verify it on all API endpoints. | Write the active session token to `.agents/state/session.json` and read it from both CLI and dashboard handlers. |
| **Complexity** | Low. Fits within python standard library (`secrets` or `uuid`) and standard HTML headers/cookies. | Medium. Requires managing file access, race conditions, file creation/deletion, and file permissions. |
| **Security Proof** | High. Token is never saved to disk. Bypasses DNS rebinding and cross-origin reads because target websites cannot read the URL query parameters of a separate tab. | Medium. Vulnerable to file leakage if workspace permissions are not restricted, and CSRF could read endpoints if credentials are sent automatically. |
| **CSRF Defense** | Excellent. Cross-origin pages cannot read local storage or query parameters of a different origin. | Low/Medium. If authentication relies on cookies, CSRF is still possible unless custom headers are enforced. |
| **DNS Rebinding Defense** | Excellent. The Host header check blocks DNS rebinding, and query tokens prevent unauthenticated access. | Excellent if combined with Host checks, otherwise vulnerable. |
| **Zero-State (DRY)** | Yes. No files written. | No. State file must be cleaned up on server exit. |

## 2. Downstream Impacts

- **Host Header Verification:** Both options require verifying the HTTP `Host` header to reject DNS Rebinding attacks. This impacts `dashboard.py` by adding a check in `is_client_allowed` verifying that `Host` matches `localhost:port` or `127.0.0.1:port`.
- **Developer UX:** Option A is completely seamless. The CLI automatically launches the default browser with the query token appended (e.g. `http://127.0.0.1:8000/?token=abc123xyz`). The client JS reads the token from the URL on load and includes it as a header `X-Session-Token` in all API fetches.
- **MCP Portability:** No impact. This is localized to the dashboard launcher.

## 3. Recommendation
**Implement Option A.** It provides zero-state, transient security that prevents CSRF and DNS Rebinding without polluting the filesystem or leaving stale session files.
