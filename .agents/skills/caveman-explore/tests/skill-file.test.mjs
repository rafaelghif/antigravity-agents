import { test } from "node:test";
import assert from "node:assert";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const skillFile = join(dirname(fileURLToPath(import.meta.url)), "..", "SKILL.md");
const md = readFileSync(skillFile, "utf8");

function frontmatter(text) {
  const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  assert.ok(match, "skill file must open with a --- frontmatter block ---");
  return match[1];
}

test("frontmatter has valid Antigravity name and description", () => {
  const fm = frontmatter(md);
  assert.match(fm, /^name:\s*caveman-explore\s*$/m, "name must be caveman-explore");
  assert.match(fm, /^description:\s*.+/m, "description required for progressive disclosure");
  assert.doesNotMatch(fm, /\b(tools|model|allowed-tools)\b/, "frontmatter must not contain legacy foreign keys");
});

test("description specifies what it does and when to invoke", () => {
  const fm = frontmatter(md);
  assert.match(fm, /cold-start|cross-file|localization/i, "must state capability");
  assert.match(fm, /use when/i, "must specify 'use when' trigger condition");
});

test("body specifies Antigravity research subagent and native tools", () => {
  assert.match(md, /TypeName:\s*"research"/i, "must specify Antigravity research subagent");
  assert.match(md, /Model:\s*"flash"/i, "must specify flash model");
  assert.match(md, /find_by_name|grep_search|view_file/i, "must cite Antigravity native tools");
  assert.match(md, /parallel/i, "must encourage parallel execution");
  assert.match(md, /ONLY an evidence block|only.*citation/i, "must mandate citation-only reply");
  assert.match(md, /path\/to\/file\.ext:START-END/i, "must show compact path:line shape");
  assert.match(md, /no relevant locations found/i, "must give honest empty fallback");
});

test("artifact carries no placeholder markers", () => {
  const banned = ["TO" + "DO", "FIX" + "ME", "place" + "holder", "X" + "X" + "X"];
  for (const marker of banned) {
    assert.doesNotMatch(md, new RegExp("\\b" + marker + "\\b", "i"), `artifact must not contain ${marker}`);
  }
});
