import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const rootDir = path.resolve('.');

test('AGENTS.md remains strictly below 12000 characters limit', () => {
  const content = fs.readFileSync(path.join(rootDir, 'AGENTS.md'), 'utf-8');
  assert.ok(content.length < 12000, `AGENTS.md length ${content.length} exceeds 12000 characters`);
  assert.match(content, /memory-management\.md/, 'AGENTS.md must list memory-management.md');
  assert.match(content, /## 8\. Agent Skills & Memory Architecture/, 'AGENTS.md must have section 8');
});

test('memory-management rule exists with trigger: always_on', () => {
  const rulePath = path.join(rootDir, '.agents', 'rules', 'memory-management.md');
  assert.ok(fs.existsSync(rulePath), 'memory-management.md must exist');
  const content = fs.readFileSync(rulePath, 'utf-8');
  assert.match(content, /trigger:\s*always_on/, 'Rule must specify trigger: always_on');
  assert.match(content, /Five-Tier Memory Hierarchy/, 'Rule must describe 5 tiers');
});

test('CONTEXT.md living domain document exists at root', () => {
  const contextPath = path.join(rootDir, 'CONTEXT.md');
  assert.ok(fs.existsSync(contextPath), 'CONTEXT.md must exist');
  const content = fs.readFileSync(contextPath, 'utf-8');
  assert.match(content, /# Antigravity Agents Domain Context/, 'Must have title');
  assert.match(content, /## 1\. Domain Glossary/, 'Must have glossary');
});

test('ADR 0001 records 5-tier memory decision', () => {
  const adrPath = path.join(rootDir, 'docs', 'adr', '0001-antigravity-5-tier-memory-system.md');
  assert.ok(fs.existsSync(adrPath), 'ADR 0001 must exist');
  const content = fs.readFileSync(adrPath, 'utf-8');
  assert.match(content, /Status:\s*Accepted/, 'ADR status must be Accepted');
});

test('docs/agents configuration files exist and are populated', () => {
  const agentDocsDir = path.join(rootDir, 'docs', 'agents');
  assert.ok(fs.existsSync(path.join(agentDocsDir, 'domain.md')), 'domain.md must exist');
  assert.ok(fs.existsSync(path.join(agentDocsDir, 'issue-tracker.md')), 'issue-tracker.md must exist');
  assert.ok(fs.existsSync(path.join(agentDocsDir, 'triage-labels.md')), 'triage-labels.md must exist');
});

test('gitignore correctly ignores .scratch contents and preserves .gitkeep', () => {
  const gitignore = fs.readFileSync(path.join(rootDir, '.gitignore'), 'utf-8');
  assert.match(gitignore, /\.scratch\/\*/, 'Must ignore .scratch/*');
  assert.match(gitignore, /!\.scratch\/\.gitkeep/, 'Must keep .scratch/.gitkeep');
  assert.match(gitignore, /handoff\.md/, 'Must ignore handoff.md');
});

test('session handoff template exists', () => {
  const templatePath = path.join(rootDir, 'docs', 'templates', 'handoff.template.md');
  assert.ok(fs.existsSync(templatePath), 'handoff.template.md must exist');
});
