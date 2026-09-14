import test from 'node:test';
import assert from 'node:assert/strict';
import { execSync } from 'node:child_process';
import path from 'node:path';
import fs from 'node:fs';
import os from 'node:os';

const rootDir = path.resolve('.');
const cliPath = path.join(rootDir, 'bin', 'cli.mjs');

test('CLI --version prints v5.0.0', () => {
  const output = execSync(`node "${cliPath}" --version`, { encoding: 'utf-8' });
  assert.match(output, /@rafaelghif\/aac v5\.0\.0/);
});

test('CLI --help prints usage banner', () => {
  const output = execSync(`node "${cliPath}" --help`, { encoding: 'utf-8' });
  assert.match(output, /USAGE:/);
  assert.match(output, /npx @rafaelghif\/aac <command>/);
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
    assert.ok(fs.existsSync(path.join(tempDir, 'AGENTS.md')), 'AGENTS.md must be scaffolded');
    assert.ok(!fs.existsSync(path.join(tempDir, 'package.json')), 'package.json MUST NEVER BE CREATED in target project');
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});
