# caveman-learn skill

Close the loop on `caveman learn`. The command measures where your agent's tokens
go; this skill reviews that plan with you and applies the fixes — one approved edit
at a time.

## Workspace Discovery

This skill is natively discovered by Google Antigravity from `.agents/skills/caveman-learn/`.

## What it does

1. Runs `caveman learn report --json` and shows your Cave Score + ranked token sinks.
2. For each sink you pick, proposes a fix and asks yes/no:
   - **reducible** (heavy `AGENTS.md`, never-invoked skill) → a concrete trim, applied
     only if it measurably lowers tokens/turn while preserving technical instructions.
   - **recurring_context** (context you re-establish every session) → offload to
     external references or documentation, leaving a clean pointer behind.
   - **load_bearing** → never touched.

3. After an approved edit passes its re-measure gate, `caveman learn applied <sink_id>`
   records the outcome in Caveman's ledger.

## Honesty

Everything is consent-gated and reversible. The analyzer never edits your files directly;
this skill proposes targeted replacements and requires user confirmation.
