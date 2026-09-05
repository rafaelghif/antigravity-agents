---
name: design
description: Use this skill for UI/UX components, CSS/Tailwind styling, WCAG 2.2 AA accessibility, design tokens, and Core Web Vitals performance optimization.
license: Apache-2.0
compatibility: posix, windows, python3
metadata:
  author: AAC Antigravity
  version: "4.47.0"
  category: design-systems
  tags: [ui, ux, tailwind, a11y, wcag, web-vitals, dtcg]
---

# UI Design, Accessibility & Web Performance Protocol

**Role**: Staff Frontend Architect & Design Systems Lead.

## Overview & Trigger Conditions
Activate this skill when creating or modifying UI components, styling layouts (CSS/Tailwind), implementing design token systems, auditing accessibility (WCAG 2.2 AA), or optimizing frontend runtime performance (Core Web Vitals).

**Trigger Scenarios & Keywords**:
- UI/UX component development, styling refactors, responsive layouts, web performance audits.
- Keywords: `ui`, `ux`, `component`, `styling`, `css`, `tailwind`, `accessibility`, `a11y`, `wcag`, `webperf`, `core web vitals`, `lcp`, `inp`, `cls`.

## Core Standards & Invariants

1. **DTCG 3-Tier Design Tokens (SSOT)**:
   - **Tier 1 (Primitive)**: Raw palette scales and fixed metrics (`colors.slate.900`, `spacing.4`).
   - **Tier 2 (Semantic)**: Intent-driven tokens (`color.bg.surface`, `color.text.muted`, `action.primary.hover`).
   - **Tier 3 (Component)**: Scoped component tokens (`button.primary.bg`, `input.border.focus`).
   - Strictly ban hardcoded hex codes (`#1e293b`) and arbitrary pixel values inside components. Map styles to design tokens or Tailwind theme utilities.

2. **WCAG 2.2 Level AA Accessibility (a11y)**:
   - **Color Contrast**: Minimum contrast ratio of $\ge 4.5:1$ for normal text, and $\ge 3:1$ for large text and interactive boundaries.
   - **Focus Visible**: NEVER remove outlines (`outline-none`) without an explicit replacement (`focus-visible:ring-2 focus-visible:ring-offset-2`). Enforced by `ui_hygiene_guard.py`.
   - **Touch Target Sizing**: Interactive elements must provide a minimum $44 \times 44\text{ px}$ target area with $\ge 8\text{px}$ spacing between adjacent targets.
   - **Semantic Markup**: All `<img>` tags must include meaningful `alt` attributes (or `alt=""` if decorative); `<button>` elements require explicit `type="button"` or `type="submit"`.

3. **Core Web Vitals & Runtime Performance**:
   - **LCP ($\le 2.5\text{s}$)**: Preload hero images (`fetchpriority="high"`). Self-host web fonts with `font-display: swap`. Eliminate render-blocking waterfalls.
   - **INP ($\le 200\text{ms}$)**: Chunk long JavaScript tasks $> 50\text{ms}$ using `scheduler.yield()`. Throttle/debounce scroll and resize listeners.
   - **CLS ($\le 0.1$)**: Always specify explicit `width`/`height` or CSS `aspect-ratio` on images, videos, and dynamic iframes.

4. **Complete 6-State Interactive Spectrum**:
   - Interactive UI primitives (buttons, inputs, cards, links) must explicitly define:
     `Default`, `Hover`, `Active / Pressed`, `Focus-Visible`, `Disabled` (`aria-disabled="true"`), and `Async` (Loading skeleton / Error recovery).

## Golden Example: Accessible Interactive Component
```html
<!-- Accessible Button with 6-State Spectrum and Design Tokens -->
<button
  type="button"
  class="min-h-[44px] min-w-[44px] px-4 py-2 text-sm font-medium rounded-md
         bg-action-primary text-white hover:bg-action-primary-hover
         active:scale-95 focus-visible:outline-none focus-visible:ring-2
         focus-visible:ring-offset-2 focus-visible:ring-action-primary
         disabled:opacity-50 disabled:pointer-events-none transition-all"
  aria-disabled="false">
  Confirm Order
</button>
```

## Procedural Workflow
1. **Token & Primitive Discovery**: Inspect existing design system tokens and reusable UI primitives before creating new components.
2. **Scaffold with Semantics**: Implement accessible HTML elements, explicit button types, and keyboard navigation.
3. **Responsive & State Audit**: Test mobile viewports, touch targets, and all 6 interactive states.
4. **Automated UI Hygiene Scan**: Run `python3 scripts/ui_hygiene_guard.py --check` to catch contrast, focus, and token violations.
5. **Local Verification**: Run `python3 scripts/verify.py --execute --terse`.

## Anti-Patterns & Common Pitfalls
- **Focus Suppression**: Using `outline-none` without an explicit `focus-visible` ring.
- **Unsized Media**: Omitting aspect-ratio or dimensions on images, causing layout shifts (CLS failure).
- **Inaccessible Non-Interactive Elements**: Adding `onClick` to `<div>` or `<span>` without keyboard handlers or ARIA role attributes.
