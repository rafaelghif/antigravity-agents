const fs = require('node:fs');

let input = '';
try {
  input = fs.readFileSync(0, 'utf-8');
} catch (e) {
  // Ignore stdin read errors
}

if (!input || !input.trim()) {
  process.stdout.write(JSON.stringify({ decision: 'allow' }));
  process.exit(0);
}

try {
  const payload = JSON.parse(input);
  const command = payload?.toolCall?.args?.CommandLine || '';
  const dangerousPatterns = [
    /\bgit\s+push\b/i,
    /\bgit\s+reset\s+--hard\b/i,
    /\bgit\s+clean\s+(-[a-zA-Z]*f[a-zA-Z]*)\b/i,
    /\bgit\s+branch\s+-D\b/i,
    /\bgit\s+checkout\s+\./i,
    /\bgit\s+restore\s+\./i,
    /--force/i,
    /reset\s+--hard/i
  ];

  for (const pattern of dangerousPatterns) {
    if (pattern.test(command)) {
      process.stdout.write(JSON.stringify({
        decision: 'deny',
        reason: `BLOCKED: '${command}' matches dangerous git pattern '${pattern.source}'. Execution blocked by Antigravity git-guardrails.`
      }));
      process.exit(0);
    }
  }
} catch (e) {
  // fallback allow on parse error
}

process.stdout.write(JSON.stringify({ decision: 'allow' }));
process.exit(0);
