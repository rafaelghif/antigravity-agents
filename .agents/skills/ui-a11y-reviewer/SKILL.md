---
name: ui-a11y-reviewer
description: Validates frontend components against WCAG accessibility standards and premium aesthetic guidelines.
---
# UI/UX & Accessibility (a11y) Reviewer Skill

## Objective
Ensure all frontend code adheres to the "Adaptive UI/UX" rules defined in AGENTS.md §3.

## When to Execute
- When generating new UI components.
- During PR reviews for frontend changes.
- **Skip Condition**: Hotfix branches that do not modify UI layouts or components.

## Execution Steps
1. Audit the UI against the explicit aesthetic criteria based on the context:
   - **For Consumer Views (Premium)**: Strict spacing (e.g., 8px grid), consistent typography scale, unbroken visual hierarchy. Micro-interactions: Hover/active states for all interactive elements. Loading indicators (spinners, skeletons).
   - **For Admin Panels**: Prioritize data density, clarity, and utilitarian design over micro-interactions.
   - **WCAG Compliance (Universal)**: Minimum contrast 4.5:1 (AA). All interactive elements MUST be keyboard-navigable and screen-reader accessible (ARIA).
2. If violations are found, immediately halt the process and refactor the code to comply before proceeding.
