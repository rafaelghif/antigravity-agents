---
name: design
description: Use this skill for UI/UX components, CSS/Tailwind styling, WCAG 2.2 AA accessibility, design tokens, and Core Web Vitals performance optimization.
---

# UI Design, Accessibility & Web Performance Protocol

<CRITICAL_DIRECTIVE>
Enforce Senior UX/UI Design Architecture, WCAG 2.2 AA accessibility, and Core Web Vitals runtime performance. Reject generic AI visual tropes, enforce 3-tier DTCG design tokens, and eliminate layout shifts.
</CRITICAL_DIRECTIVE>

<ENTERPRISE_STANDARDS>
1. **DTCG 3-Tier Design Tokens (SSOT)**:
   - **Tier 1 (Primitive)**: Raw palette and scales (`colors.slate.900`, `spacing.4`).
   - **Tier 2 (Semantic)**: Intent-driven tokens (`color.bg.surface`, `color.text.muted`, `action.primary.hover`).
   - **Tier 3 (Component)**: Scoped component tokens (`button.primary.bg`, `input.border.focus`).
   - Strictly ban raw color hex codes or arbitrary pixel margins in component files. Map to tokens or Tailwind theme classes.
2. **WCAG 2.2 Level AA Accessibility (a11y)**:
   - **Contrast**: $\ge 4.5:1$ for normal text, $\ge 3:1$ for large text and interactive boundaries.
   - **Focus Visible**: NEVER use `outline-none` without an explicit focus ring (`focus-visible:ring-2`). Auto-checked by `ui_hygiene_guard.py`.
   - **Touch Target**: Interactive elements must meet minimum $44 \times 44\text{ px}$ target size on touch viewports.
   - **Semantics**: All `<img>` must have `alt` text; buttons require explicit `type="button"`; decorative icons use `aria-hidden="true"`.
3. **Core Web Vitals & Web Performance**:
   - **LCP ($\le 2.5\text{s}$)**: Prioritize hero images (`fetchpriority="high"`, `priority`). Self-host fonts with `font-display: swap`. Avoid client-side rendering waterfalls.
   - **INP ($\le 200\text{ms}$)**: Break tasks $> 50\text{ms}$ using `scheduler.yield()` or microtask chunking. Debounce/throttle scroll and resize events.
   - **CLS ($\le 0.1$)**: Always declare explicit `width` and `height` or CSS `aspect-ratio` on all `<img>`, `<video>`, and dynamic containers to prevent layout jumps.
4. **Bundle Hygiene & Code-Splitting**:
   - Ban barrel imports that pull entire libraries. Use path imports (`import debounce from 'lodash/debounce'`).
   - Lazy load heavy modals and visualization charts via dynamic `import()` or `React.lazy()`.
5. **Complete 6-State Interactive Spectrum**:
   - Interactive components must define: 1) Default, 2) Hover, 3) Active/Pressed, 4) Focus-Visible, 5) Disabled (`aria-disabled`), and 6) Async States (Skeleton/Loading, Empty CTA, Error recovery).
</ENTERPRISE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Token & Component Discovery**: Inspect existing design tokens and reusable UI primitives.
2. **Scaffold with Semantics**: Build using semantic HTML, explicit button types, and keyboard navigability.
3. **Performance Audit**: Ensure explicit image dimensions, path imports, and lazy loading.
4. **Verification**: Run `python3 scripts/ui_hygiene_guard.py --check` and `python3 scripts/verify.py --execute`.
</PROCEDURAL_WORKFLOW>
