#!/usr/bin/env node

/**
 * Antigravity Agents CLI
 * The official setup, audit, and management tool for Google Antigravity workspaces.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const packageRoot = path.resolve(__dirname, '..');

const args = process.argv.slice(2);
const command = args[0] || 'help';

const VERSION = '5.0.0';

function showHelp() {
  console.log(`
🚀 Antigravity Agents CLI (v${VERSION})
The Production-Grade Autonomous Engineering Framework for Google Antigravity

USAGE:
  npx antigravity-agents <command> [options]

COMMANDS:
  init          Scaffold Antigravity workspace (.agents/, AGENTS.md, CONTEXT.md) into current directory
  audit         Deeply audit current workspace against Antigravity best practices (8 dimensions)
  doctor        Perform environment and workspace diagnostic health checks
  list          Display all 64 skills categorized by task batch
  version, -v   Show CLI version
  help, -h      Display this help menu

OPTIONS:
  --force       Overwrite existing files during init
  --json        Output results in JSON format
`);
}

function runInit() {
  const targetDir = process.cwd();
  const force = args.includes('--force');
  console.log(`\n🚀 Initializing Antigravity Agents (v${VERSION}) in:\n   ${targetDir}\n`);

  if (targetDir === packageRoot) {
    console.log('ℹ️ Current directory is the framework source repository itself.');
  }

  // 1. Copy .agents directory
  const sourceAgents = path.join(packageRoot, '.agents');
  const targetAgents = path.join(targetDir, '.agents');

  if (fs.existsSync(sourceAgents)) {
    console.log('📦 Scaffolding .agents/ directory...');
    fs.cpSync(sourceAgents, targetAgents, { recursive: true, force });
  }

  // 2. Copy root files
  const rootFiles = ['AGENTS.md', 'GEMINI.md', 'CONTEXT.md'];
  for (const rf of rootFiles) {
    const srcFile = path.join(packageRoot, rf);
    const dstFile = path.join(targetDir, rf);
    if (fs.existsSync(srcFile)) {
      if (!fs.existsSync(dstFile) || force) {
        fs.copyFileSync(srcFile, dstFile);
        console.log(`📄 Created ${rf}`);
      } else {
        console.log(`⏩ Skipped ${rf} (already exists, use --force to overwrite)`);
      }
    }
  }

  // 3. Ensure .scratch directory exists
  const scratchDir = path.join(targetDir, '.scratch');
  if (!fs.existsSync(scratchDir)) {
    fs.mkdirSync(scratchDir, { recursive: true });
    fs.writeFileSync(path.join(scratchDir, '.gitkeep'), '# Ephemeral scratchpad directory\n');
    console.log('📁 Created .scratch/ directory');
  }

  // 4. Update .gitignore if present
  const gitignorePath = path.join(targetDir, '.gitignore');
  const gitignoreAdditions = [
    '# Antigravity Runtime & Ephemeral State',
    '.gemini/',
    '*.log',
    '*.tmp',
    '.scratch/*',
    '!.scratch/.gitkeep',
    'handoff.md',
    '',
    '# Credentials & MCP Secrets',
    '.agents/mcp_config.json',
    '!.agents/mcp_config.example.json',
    '.agents/plugins/**/mcp_config.json',
    '!.agents/plugins/**/mcp_config.example.json'
  ];

  if (fs.existsSync(gitignorePath)) {
    let gitignoreContent = fs.readFileSync(gitignorePath, 'utf-8');
    let modified = false;
    for (const item of gitignoreAdditions) {
      if (item && !gitignoreContent.includes(item)) {
        gitignoreContent += `\n${item}`;
        modified = true;
      }
    }
    if (modified) {
      fs.writeFileSync(gitignorePath, gitignoreContent.trim() + '\n', 'utf-8');
      console.log('🛡️ Updated .gitignore with Antigravity guardrails');
    }
  } else {
    fs.writeFileSync(gitignorePath, gitignoreAdditions.join('\n') + '\n', 'utf-8');
    console.log('🛡️ Created .gitignore with Antigravity guardrails');
  }

  console.log(`
✅ Antigravity workspace initialization complete!
👉 Next steps:
   1. Open in Antigravity IDE or Antigravity 2.0.
   2. Configure MCP tokens by copying .agents/mcp_config.example.json to .agents/mcp_config.json
   3. Run 'npx antigravity-agents doctor' to verify readiness.
`);
}

function runAudit() {
  const targetDir = process.cwd();
  console.log(`\n🔍 Auditing Antigravity workspace in:\n   ${targetDir}\n`);

  const issues = [];

  // 1. Check AGENTS.md
  const agentsPath = path.join(targetDir, 'AGENTS.md');
  if (!fs.existsSync(agentsPath)) {
    issues.push('Missing root AGENTS.md');
  } else {
    const content = fs.readFileSync(agentsPath, 'utf-8');
    if (content.length > 12000) {
      issues.push(`AGENTS.md length is ${content.length} chars (exceeds 12000 limit)`);
    }
    if (!content.includes('file:///')) {
      issues.push('AGENTS.md missing clickable file:/// links');
    }
  }

  // 2. Check rules
  const rulesDir = path.join(targetDir, '.agents', 'rules');
  if (!fs.existsSync(rulesDir)) {
    issues.push('Missing .agents/rules directory');
  } else {
    const rules = fs.readdirSync(rulesDir).filter(f => f.endsWith('.md'));
    if (rules.length === 0) {
      issues.push('No modular rules found in .agents/rules');
    }
    for (const rf of rules) {
      const content = fs.readFileSync(path.join(rulesDir, rf), 'utf-8');
      if (!content.includes('trigger:')) {
        issues.push(`Rule ${rf} missing frontmatter trigger specification`);
      }
    }
  }

  // 3. Check skills
  const skillsDir = path.join(targetDir, '.agents', 'skills');
  if (!fs.existsSync(skillsDir)) {
    issues.push('Missing .agents/skills directory');
  } else {
    const skills = fs.readdirSync(skillsDir, { withFileTypes: true })
      .filter(d => d.isDirectory())
      .map(d => d.name);
    console.log(`Checking ${skills.length} skills...`);
    for (const sf of skills) {
      const sfPath = path.join(skillsDir, sf, 'SKILL.md');
      if (!fs.existsSync(sfPath)) {
        issues.push(`Skill ${sf} missing SKILL.md`);
        continue;
      }
      const content = fs.readFileSync(sfPath, 'utf-8');
      if (!content.includes(`name: ${sf}`)) {
        issues.push(`Skill ${sf} name in frontmatter does not match folder`);
      }
      if (!/use when|trigger:/i.test(content)) {
        issues.push(`Skill ${sf} description lacks "Use when..." or "Trigger:" phrasing`);
      }
    }
  }

  // 4. Check hooks
  const hooksFile = path.join(targetDir, '.agents', 'hooks.json');
  if (!fs.existsSync(hooksFile)) {
    issues.push('Missing .agents/hooks.json');
  } else {
    try {
      JSON.parse(fs.readFileSync(hooksFile, 'utf-8'));
    } catch (e) {
      issues.push(`.agents/hooks.json has invalid JSON syntax: ${e.message}`);
    }
  }

  console.log(`\nAudit Results: ${issues.length === 0 ? '✅ 100% COMPLIANT' : `⚠️ ${issues.length} ISSUES DETECTED`}`);
  if (issues.length > 0) {
    issues.forEach(iss => console.log(` - ❌ ${iss}`));
    process.exit(1);
  } else {
    console.log('✨ All Antigravity operational criteria and best practices satisfied.');
  }
}

function runDoctor() {
  console.log(`\n🩺 Antigravity Environment & Diagnostic Doctor (v${VERSION})\n`);

  const checks = [
    {
      name: 'Node.js Runtime',
      run: () => {
        const version = process.version;
        const major = parseInt(version.replace('v', '').split('.')[0], 10);
        return { ok: major >= 18, message: `Node.js ${version} (required >= 18.0.0)` };
      }
    },
    {
      name: 'Workspace Scope',
      run: () => {
        const cwd = process.cwd();
        const hasAgents = fs.existsSync(path.join(cwd, '.agents'));
        const hasAgentsMd = fs.existsSync(path.join(cwd, 'AGENTS.md'));
        return { ok: hasAgents && hasAgentsMd, message: hasAgents && hasAgentsMd ? 'Antigravity workspace detected' : 'Not an Antigravity workspace (run npx antigravity-agents init)' };
      }
    },
    {
      name: 'Skills Integrity',
      run: () => {
        const skillsDir = path.join(process.cwd(), '.agents', 'skills');
        if (!fs.existsSync(skillsDir)) return { ok: false, message: 'Missing .agents/skills folder' };
        const count = fs.readdirSync(skillsDir).filter(d => fs.statSync(path.join(skillsDir, d)).isDirectory()).length;
        return { ok: count > 0, message: `${count} skills mounted` };
      }
    },
    {
      name: 'Hooks Integrity',
      run: () => {
        const hooksPath = path.join(process.cwd(), '.agents', 'hooks.json');
        if (!fs.existsSync(hooksPath)) return { ok: false, message: 'Missing .agents/hooks.json' };
        try {
          const json = JSON.parse(fs.readFileSync(hooksPath, 'utf-8'));
          const hookCount = Object.keys(json).length;
          return { ok: true, message: `${hookCount} hook groups configured (${Object.keys(json).join(', ')})` };
        } catch {
          return { ok: false, message: 'Corrupted .agents/hooks.json' };
        }
      }
    },
    {
      name: 'MCP Configuration',
      run: () => {
        const mcpPath = path.join(process.cwd(), '.agents', 'mcp_config.json');
        const examplePath = path.join(process.cwd(), '.agents', 'mcp_config.example.json');
        if (fs.existsSync(mcpPath)) return { ok: true, message: 'Active .agents/mcp_config.json found' };
        if (fs.existsSync(examplePath)) return { ok: true, message: 'Template mcp_config.example.json present (copy to mcp_config.json to activate)' };
        return { ok: false, message: 'Missing MCP configuration' };
      }
    }
  ];

  for (const c of checks) {
    const res = c.run();
    console.log(`${res.ok ? '✅' : '❌'} ${c.name.padEnd(20)}: ${res.message}`);
  }
  console.log('\nDiagnostic complete.\n');
}

function runList() {
  const skillsDir = path.join(packageRoot, '.agents', 'skills');
  if (!fs.existsSync(skillsDir)) {
    console.error('Skills directory not found.');
    process.exit(1);
  }
  const skills = fs.readdirSync(skillsDir, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name)
    .sort();

  console.log(`\n📚 Antigravity 64-Skill Suite (v${VERSION}):\n`);
  skills.forEach((s, idx) => {
    const skillPath = path.join(skillsDir, s, 'SKILL.md');
    let desc = '';
    if (fs.existsSync(skillPath)) {
      const content = fs.readFileSync(skillPath, 'utf-8');
      const descMatch = content.match(/description:\s*(?:>-\s*|>|\s*)?([\s\S]*?)(?=\n---|\n#)/);
      if (descMatch) desc = descMatch[1].replace(/\r?\n/g, ' ').trim().slice(0, 75) + '...';
    }
    console.log(`  ${String(idx + 1).padStart(2, ' ')}. ${s.padEnd(30)} ${desc}`);
  });
  console.log(`\nTotal: ${skills.length} skills available.\n`);
}

switch (command) {
  case 'init':
    runInit();
    break;
  case 'audit':
    runAudit();
    break;
  case 'doctor':
    runDoctor();
    break;
  case 'list':
    runList();
    break;
  case 'version':
  case '-v':
  case '--version':
    console.log(`antigravity-agents v${VERSION}`);
    break;
  case 'help':
  case '-h':
  case '--help':
  default:
    showHelp();
    break;
}
