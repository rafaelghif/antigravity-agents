---
name: design
description: Use this skill when the user asks to modify or create UI components, apply CSS styling, manage frontend architectures, or debug visual issues.
---

<CRITICAL_DIRECTIVE>
Enforce Senior UX/UI Design Architecture (inspired by DTCG tokens, WCAG 2.2 AA, and anti-slop doctrine). Reject generic AI visual tropes, enforce strict design tokens, and guarantee accessible, production-grade components.
</CRITICAL_DIRECTIVE>

<ENTERPRISE_STANDARDS>
1. **DTCG 3-Tier Design Tokens (SSOT)**:
   - **Tier 1 (Primitive)**: Raw palette and scales (`colors.slate.900`, `spacing.4`).
   - **Tier 2 (Semantic)**: Intent-driven tokens (`color.bg.surface`, `color.text.muted`, `action.primary.hover`).
   - **Tier 3 (Component)**: Scoped component tokens (`button.primary.bg`, `input.border.focus`).
   - **Zero Hardcoded Values**: Strictly ban raw color hex codes (e.g. `#3b82f6`) or arbitrary pixel values in component files. Map everything to design tokens or Tailwind semantic utility classes.

2. **WCAG 2.2 Level AA Accessibility (a11y)**:
   - **Contrast Ratio**: $\ge 4.5:1$ for normal text, $\ge 3:1$ for large text ($\ge 18\text{pt}$ / $14\text{pt}$ bold) and UI components.
   - **Focus Visible**: NEVER use `outline-none` or `outline: none` without an explicit focus indicator (e.g. `focus-visible:ring-2 focus-visible:ring-offset-2`). Auto-checked by `scripts/ui_hygiene_guard.py`.
   - **Minimum Touch Target**: Interactive elements must meet minimum $44 \times 44\text{ px}$ target size on mobile.
   - **Semantic & ARIA Standards**: All `<img>` MUST have informative `alt` text. Interactive controls must declare `type="button"`, `aria-expanded`, `aria-controls`, and `role` appropriately. Decorative icons must have `aria-hidden="true"`.
   - **Reduced Motion**: Respect user preferences; provide `motion-reduce:transition-none` or `@media (prefers-reduced-motion: reduce)` fallbacks.

3. **Anti-AI-Slop Visual Taste Doctrine**:
   - **Ban AI Tropes**: Forbid generic purple/indigo gradients everywhere, low-contrast gray text on dark backgrounds (`#6B7280` on `#111827`), and over-blurred backdrop filters.
   - **Visual Hierarchy & Typography**: Enforce clear scale contrasts between Headings, Body, and Captions. Use intentional whitespace and consistent 8px grid spacing.
   - **Micro-Interactions**: Smooth state transitions ($150\text{ms}$ - $250\text{ms}$ ease-out), tactile active states, and non-jarring hover feedback.

4. **Complete 6-State Spectrum**:
   Every interactive component MUST define all 6 lifecycle states:
   1) **Default**, 2) **Hover**, 3) **Active/Pressed**, 4) **Focus-Visible**, 5) **Disabled** (`aria-disabled`), and 6) **Async States** (Skeleton/Shimmer loading, Empty state with actionable CTA, and Error recovery banner).

5. **Nielsen's Heuristics & UX Writing**:
   - Instant feedback on every user interaction (loading states, toast confirmation).
   - Actionable error copy formula: `[What happened]` + `[Why it occurred]` + `[Action to resolve]`. Never output "Something went wrong".
</ENTERPRISE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Design System & Token Discovery**: Inspect existing tokens and UI libraries (`grep_search` in `components/`, `ui/`, `styles/`, `tailwind.config.*`).
2. **Component Reuse & Atomic Fit**: Reuse existing project primitives (`Button`, `Dialog`, `Input`, `Card`). Do NOT write duplicate one-off primitives.
3. **Scaffold with Accessible Semantics**: Build using semantic HTML, explicit button types, and keyboard navigability.
4. **Interactive State & Contrast Audit**: Verify focus rings, contrast ratios, and touch targets. Run `python3 scripts/ui_hygiene_guard.py --check`.
5. **Diff Review**: Ensure zero hardcoded hex styles, zero outline-none regressions, and 100% token consistency.
</PROCEDURAL_WORKFLOW>

<L9_STANDARDS>
- **Component Reusability**: Extract repetitive UI into atomic components.
- **Design Tokens**: 3-tier hierarchy (Primitive -> Semantic -> Component). No hardcoded hex.
- **Accessibility (a11y)**: WCAG 2.2 AA compliance, visible focus rings, and screen-reader semantics are non-negotiable.
</L9_STANDARDS>
