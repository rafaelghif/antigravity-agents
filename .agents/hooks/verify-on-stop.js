const fs = require('fs');
const { execSync } = require('child_process');

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
  if (payload.terminationReason === 'model_stop') {
    try {
      execSync('node --test tests/memory-system.test.mjs', { stdio: 'pipe' });
    } catch (err) {
      process.stdout.write(JSON.stringify({
        decision: 'continue',
        reason: 'Quality Gate Failed: Unit tests in tests/memory-system.test.mjs are failing. Please fix regressions before concluding.'
      }));
      process.exit(0);
    }
  }
} catch (e) {
  // Fallback to allow on JSON parse errors
}

process.stdout.write(JSON.stringify({ decision: 'allow' }));
process.exit(0);
