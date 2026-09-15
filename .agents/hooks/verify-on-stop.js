import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execSync } from 'node:child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

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
    const rootDir = (payload.workspacePaths && payload.workspacePaths[0]) ? path.resolve(payload.workspacePaths[0]) : path.resolve(__dirname, '..', '..');
    const testFile = path.join(rootDir, 'tests', 'memory-system.test.mjs');
    if (fs.existsSync(testFile)) {
      try {
        const testEnv = { ...process.env };
        delete testEnv.NODE_TEST_CONTEXT;
        delete testEnv.NODE_TEST_WORKER_ID;
        execSync(`node --test "${testFile}"`, { cwd: rootDir, stdio: 'pipe', env: testEnv });
      } catch (err) {
        process.stdout.write(JSON.stringify({
          decision: 'continue',
          reason: 'Quality Gate Failed: Unit tests are failing. Please fix regressions before concluding.'
        }));
        process.exit(0);
      }
    }
  }
} catch (e) {
  // Fallback to allow on JSON parse errors
}

process.stdout.write(JSON.stringify({ decision: 'allow' }));
process.exit(0);
