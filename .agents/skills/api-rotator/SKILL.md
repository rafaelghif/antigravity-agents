---
name: api-rotator
description: Auto-rotate API keys and profiles when encountering rate-limiting
scripts:
  - scripts/main.py
---

# api-rotator Skill

This skill provides a high-fidelity wrapper script in Python to execute agent LLM API calls with built-in hybrid rotation. It proactively checks the token budget for the active profile before requests and reactively rotates profiles on rate limits (HTTP 429).

## 1. Input Specification
- `--prompt` (`-p`): Prompt text to send to the LLM (default: "Hello, World!").
- `--provider`: LLM provider (`gemini` or `openai`).
- `--model`: Model name to use.
- `--tokens`: Quota/token consumption count to log upon successful execution (default: 150).
- `--simulate-limit`: Simulated rate-limit retry count (useful for testing rotation without API keys).
- `--debug`: Enable verbose debug logging.

## 2. Operational Procedures
1. Ensure API profiles are configured in `.agents/api_keys`.
2. Activate a profile using `./.agents/scripts/helper.sh api-profile [name]`.
3. Run the rotator skill:
   ```bash
   python3 .agents/skills/api-rotator/scripts/main.py --prompt "Test prompt" --simulate-limit 1
   ```
4. Verify that the script automatically rotates to the next profile, reloads the keys, retries, and successfully outputs the result.

## 3. Decision Matrix
- **Check Budget**: If the active profile's token budget is exhausted, rotate to the next profile.
- **Catch Rate Limit**: If the execution fails with HTTP 429 or equivalent quota error, rotate the profile, reload, and retry.
- **Log Usage**: If successful, log the token usage under the active profile name.

## 4. Error Mitigation Tree
- If all profiles are exhausted or an unhandled exception occurs, log the error details and exit with status code 1.

## 5. Output Verification Gate
- [x] Executable script auto-rotates keys successfully under rate-limiting simulation.
