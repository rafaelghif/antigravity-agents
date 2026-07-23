---
name: ui-a11y-reviewer
description: Frontend component validator against WCAG standards and aesthetic guidelines.
instruction: Use when generating new UI components or during PR reviews for frontend changes to validate accessibility and UX.
requires_core: ">=4.0.0"
---
# UI/UX & Accessibility (a11y) Reviewer Skill

## Objective
Ensure all frontend code adheres to the "Adaptive UI/UX" rules defined in AGENTS.md.

## When to Execute
- When generating new UI components.
- During PR reviews for frontend changes.
- **Objective Skip Conditions**: No modifications to `.html`, `.jsx`, `.tsx`, `.css`, `.scss`, `.vue`, `.svelte` files. No modifications to `public/` or `static/` assets. (Exception: Documentation-only changes).

## Execution Steps
1. Audit the UI against the explicit aesthetic criteria based on the context:
   - **For Consumer Views**: Evaluate visual hierarchy (F-pattern or Z-pattern), consistent spacing system (read grid size from `.agents/config.json`), and micro-interactions (hover, focus, transition states < 300ms).
   - **For Admin Panels**: Evaluate data density (maximize information) and utility (bulk actions, filtering, sorting).
   - **WCAG Compliance**: Verify contrast (`axe-core` or `pa11y`), keyboard navigation (manual tab test to `.agents/scratch/a11y-test-<date>.md`), and ARIA properties (`eslint-plugin-jsx-a11y`).
   - **Responsive Design**: Verify UI works at the viewports defined in `.agents/config.json` (Use Puppeteer/Playwright in the toolchain for automated viewport testing). Images use `srcset`. No horizontal scrolling.
2. If violations are found, immediately halt the process and refactor the code to comply before proceeding.
