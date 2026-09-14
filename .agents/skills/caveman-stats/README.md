# caveman-stats

Real session token receipts and turn analytics for Google Antigravity.

## What it does

Inspects the Antigravity session transcript (`transcript.jsonl`) to report real turn counts, active caveman compression levels, and calculated token savings versus verbose baseline responses.

## How to invoke

```
/caveman-stats
```

## Example output

```
Session Turns:    18
Caveman Mode:     full (active)
Est. Gross Saved: ~55% output tokens
Rule Overhead:    ~225 tokens/turn
Net Economy:      Positive
```

## See also

- [`SKILL.md`](./SKILL.md) — execution procedure
- [AGENTS.md](../../../AGENTS.md) — workspace root guidelines
