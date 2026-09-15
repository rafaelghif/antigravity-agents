import test from 'node:test';
import assert from 'node:assert/strict';
import { execSync } from 'node:child_process';
import path from 'node:path';
import fs from 'node:fs';
import os from 'node:os';

const rootDir = path.resolve('.');
const cliPath = path.join(rootDir, 'bin', 'cli.mjs');

test('CLI --version prints v5.0.3', () => {
  const output = execSync(`node "${cliPath}" --version`, { encoding: 'utf-8' });
  assert.match(output, /@rafaelghif\/aac-core v5\.0\.3/);
});

test('CLI --help prints usage banner', () => {
  const output = execSync(`node "${cliPath}" --help`, { encoding: 'utf-8' });
  assert.match(output, /USAGE:/);
  assert.match(output, /npx @rafaelghif\/aac-core <command>/);
  assert.match(output, /init/);
  assert.match(output, /audit/);
  assert.match(output, /doctor/);
  assert.match(output, /list/);
});

test('CLI list displays skills count', () => {
  const output = execSync(`node "${cliPath}" list`, { encoding: 'utf-8' });
  assert.match(output, /Total: 64 skills available/);
});

test('CLI doctor performs environment health checks', () => {
  const output = execSync(`node "${cliPath}" doctor`, { encoding: 'utf-8' });
  assert.match(output, /Node\.js Runtime/);
  assert.match(output, /Workspace Scope/);
  assert.match(output, /Skills Integrity/);
  assert.match(output, /Hooks Integrity/);
});

test('CLI init never creates or overwrites package.json in target directory', () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'antigravity-test-'));
  try {
    execSync(`node "${cliPath}" init`, { cwd: tempDir, encoding: 'utf-8' });
    assert.ok(fs.existsSync(path.join(tempDir, '.agents')), '.agents/ must be scaffolded');
    assert.ok(fs.existsSync(path.join(tempDir, 'docs')), 'docs/ must be scaffolded');
    assert.ok(fs.existsSync(path.join(tempDir, 'AGENTS.md')), 'AGENTS.md must be scaffolded');
    assert.ok(fs.existsSync(path.join(tempDir, 'GEMINI.md')), 'GEMINI.md must be scaffolded');
    assert.ok(fs.existsSync(path.join(tempDir, 'CLAUDE.md')), 'CLAUDE.md must be scaffolded');
    assert.ok(fs.existsSync(path.join(tempDir, 'CONTEXT.md')), 'CONTEXT.md must be scaffolded');
    assert.ok(fs.existsSync(path.join(tempDir, 'skills-lock.json')), 'skills-lock.json must be scaffolded');
    assert.ok(fs.existsSync(path.join(tempDir, '.scratch')), '.scratch/ must be scaffolded');
    assert.ok(fs.existsSync(path.join(tempDir, '.scratch', '.gitkeep')), '.scratch/.gitkeep must be scaffolded');
    assert.ok(fs.existsSync(path.join(tempDir, '.gitignore')), '.gitignore must be scaffolded');
    assert.ok(!fs.existsSync(path.join(tempDir, 'package.json')), 'package.json MUST NEVER BE CREATED in target project');
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('install.ps1 scaffolds workspace with zero package.json pollution', (t) => {
  if (process.platform !== 'win32') {
    t.skip('PowerShell test requires Windows');
    return;
  }
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'aac-ps1-test-'));
  const ps1Script = path.join(rootDir, 'install.ps1');
  try {
    execSync(`powershell -ExecutionPolicy Bypass -File "${ps1Script}"`, { cwd: tempDir, encoding: 'utf-8' });
    assert.ok(fs.existsSync(path.join(tempDir, '.agents')), '.agents/ must be scaffolded by install.ps1');
    assert.ok(fs.existsSync(path.join(tempDir, 'docs')), 'docs/ must be scaffolded by install.ps1');
    assert.ok(fs.existsSync(path.join(tempDir, 'AGENTS.md')), 'AGENTS.md must be scaffolded by install.ps1');
    assert.ok(fs.existsSync(path.join(tempDir, 'GEMINI.md')), 'GEMINI.md must be scaffolded by install.ps1');
    assert.ok(fs.existsSync(path.join(tempDir, 'CLAUDE.md')), 'CLAUDE.md must be scaffolded by install.ps1');
    assert.ok(fs.existsSync(path.join(tempDir, 'CONTEXT.md')), 'CONTEXT.md must be scaffolded by install.ps1');
    assert.ok(fs.existsSync(path.join(tempDir, 'skills-lock.json')), 'skills-lock.json must be scaffolded by install.ps1');
    assert.ok(fs.existsSync(path.join(tempDir, '.scratch')), '.scratch/ must be scaffolded by install.ps1');
    assert.ok(fs.existsSync(path.join(tempDir, '.scratch', '.gitkeep')), '.scratch/.gitkeep must be scaffolded by install.ps1');
    assert.ok(fs.existsSync(path.join(tempDir, '.gitignore')), '.gitignore must be scaffolded by install.ps1');
    assert.ok(!fs.existsSync(path.join(tempDir, 'package.json')), 'package.json MUST NEVER BE CREATED by install.ps1');
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('install.sh scaffolds workspace with zero package.json pollution', (t) => {
  let canRunBash = false;
  const isWindows = process.platform === 'win32';

  if (isWindows) {
    try {
      execSync('wsl bash -c "echo OK"', { stdio: 'pipe' });
      canRunBash = true;
    } catch {
      canRunBash = false;
    }
  } else {
    try {
      execSync('bash -c "echo OK"', { stdio: 'pipe' });
      canRunBash = true;
    } catch {
      canRunBash = false;
    }
  }

  if (!canRunBash) {
    t.skip('bash/wsl is not available in environment');
    return;
  }

  if (isWindows) {
    const testDirName = 'aac-sh-' + Date.now();
    try {
      const script = `/mnt/d/Project/antigravity-agents/install.sh`;
      execSync(`wsl bash -c "mkdir -p /tmp/${testDirName} && cd /tmp/${testDirName} && ${script}"`, { encoding: 'utf-8' });
      const checkFiles = execSync(`wsl bash -c "test -d /tmp/${testDirName}/.agents && test -d /tmp/${testDirName}/docs && test -f /tmp/${testDirName}/AGENTS.md && test -f /tmp/${testDirName}/GEMINI.md && test -f /tmp/${testDirName}/CLAUDE.md && test -f /tmp/${testDirName}/CONTEXT.md && test -f /tmp/${testDirName}/skills-lock.json && test -d /tmp/${testDirName}/.scratch && test -f /tmp/${testDirName}/.scratch/.gitkeep && test -f /tmp/${testDirName}/.gitignore && test ! -f /tmp/${testDirName}/package.json && echo ALL_PASSED"`, { encoding: 'utf-8' });
      assert.match(checkFiles, /ALL_PASSED/);
    } finally {
      execSync(`wsl bash -c "rm -rf /tmp/${testDirName}"`, { stdio: 'pipe' });
    }
  } else {
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'aac-sh-test-'));
    try {
      execSync(`bash "${path.join(rootDir, 'install.sh')}"`, { cwd: tempDir, encoding: 'utf-8' });
      assert.ok(fs.existsSync(path.join(tempDir, '.agents')), '.agents/ must be scaffolded by install.sh');
      assert.ok(fs.existsSync(path.join(tempDir, 'docs')), 'docs/ must be scaffolded by install.sh');
      assert.ok(fs.existsSync(path.join(tempDir, 'AGENTS.md')), 'AGENTS.md must be scaffolded by install.sh');
      assert.ok(fs.existsSync(path.join(tempDir, 'GEMINI.md')), 'GEMINI.md must be scaffolded by install.sh');
      assert.ok(fs.existsSync(path.join(tempDir, 'CLAUDE.md')), 'CLAUDE.md must be scaffolded by install.sh');
      assert.ok(fs.existsSync(path.join(tempDir, 'CONTEXT.md')), 'CONTEXT.md must be scaffolded by install.sh');
      assert.ok(fs.existsSync(path.join(tempDir, 'skills-lock.json')), 'skills-lock.json must be scaffolded by install.sh');
      assert.ok(fs.existsSync(path.join(tempDir, '.scratch')), '.scratch/ must be scaffolded by install.sh');
      assert.ok(fs.existsSync(path.join(tempDir, '.scratch', '.gitkeep')), '.scratch/.gitkeep must be scaffolded by install.sh');
      assert.ok(fs.existsSync(path.join(tempDir, '.gitignore')), '.gitignore must be scaffolded by install.sh');
      assert.ok(!fs.existsSync(path.join(tempDir, 'package.json')), 'package.json MUST NEVER BE CREATED by install.sh');
    } finally {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  }
});

test('lifecycle hook block-dangerous-git.cjs blocks dangerous git commands', () => {
  const hookScript = path.join(rootDir, '.agents', 'hooks', 'block-dangerous-git.cjs');
  const testCases = [
    { cmd: 'git push origin main', blocked: true },
    { cmd: 'git reset --hard HEAD~1', blocked: true },
    { cmd: 'git clean -fd', blocked: true },
    { cmd: 'git branch -D feat-branch', blocked: true },
    { cmd: 'git status', blocked: false },
    { cmd: 'git add .', blocked: false },
    { cmd: 'git commit -m "feat: valid commit"', blocked: false }
  ];

  for (const tc of testCases) {
    const payload = JSON.stringify({
      toolCall: { name: 'run_command', args: { CommandLine: tc.cmd } }
    });
    const output = execSync(`node "${hookScript}"`, { input: payload, encoding: 'utf-8' });
    const result = JSON.parse(output);
    if (tc.blocked) {
      assert.equal(result.decision, 'deny', `Expected '${tc.cmd}' to be blocked`);
    } else {
      assert.equal(result.decision, 'allow', `Expected '${tc.cmd}' to be allowed`);
    }
  }
});

test('lifecycle hook verify-on-stop.cjs executes quality gate on model_stop', () => {
  const hookScript = path.join(rootDir, '.agents', 'hooks', 'verify-on-stop.cjs');
  const payload = JSON.stringify({
    terminationReason: 'model_stop',
    workspacePaths: [rootDir]
  });
  const output = execSync(`node "${hookScript}"`, { input: payload, encoding: 'utf-8' });
  const result = JSON.parse(output);
  assert.equal(result.decision, 'allow', 'Stop hook should allow when tests pass');
});

test('lifecycle hook verify-on-stop.cjs returns continue when tests fail', () => {
  const hookScript = path.join(rootDir, '.agents', 'hooks', 'verify-on-stop.cjs');
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'aac-fail-test-'));
  try {
    fs.mkdirSync(path.join(tempDir, 'tests'), { recursive: true });
    fs.writeFileSync(
      path.join(tempDir, 'tests', 'memory-system.test.mjs'),
      'import test from "node:test"; import assert from "node:assert/strict"; test("returns continue failing test", () => { assert.fail("simulated failure"); });\n'
    );
    const payload = JSON.stringify({
      terminationReason: 'model_stop',
      workspacePaths: [tempDir]
    });
    const cleanEnv = { ...process.env };
    delete cleanEnv.NODE_TEST_CONTEXT;
    delete cleanEnv.NODE_TEST_WORKER_ID;
    const output = execSync(`node "${hookScript}"`, { input: payload, encoding: 'utf-8', env: cleanEnv });
    const result = JSON.parse(output);
    assert.equal(result.decision, 'continue', 'Stop hook should return continue to block stop when tests fail');
    assert.match(result.reason, /Quality Gate Failed/, 'Should provide failure reason');
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});


