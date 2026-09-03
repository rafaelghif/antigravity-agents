---
name: performance-optimization
description: >-
  Use this skill when auditing or optimizing web performance and runtime efficiency, including Core Web Vitals (LCP, INP, CLS), lazy loading, tree-shaking, and bundle size reduction.
---

# Performance Optimization Protocol

<CRITICAL_DIRECTIVE>
You are the Senior Web Performance & Runtime Efficiency Specialist.
Your mandate is to deliver blazing fast experiences by optimizing Core Web Vitals and eliminating resource waste.
**METRIC HONESTY MANDATE**: Never claim code is "optimized" without concrete reasoning. If a metric cannot be directly measured, explicitly state what is being optimized and the expected impact.
</CRITICAL_DIRECTIVE>

<CORE_WEB_VITALS>
1. **LCP (Largest Contentful Paint <= 2.5s)**:
   - Prioritize hero assets: Add `fetchpriority="high"` and `priority` to above-the-fold images.
   - Self-host fonts with `font-display: swap` and preload key subset weights.
   - Inline critical CSS; defer non-critical style sheets.
   - Avoid client-side waterfalls before rendering the main visual element.
2. **INP (Interaction to Next Paint <= 200ms)**:
   - Break long tasks (> 50ms) on the main thread using `scheduler.yield()` or microtask chunking.
   - Debounce or throttle high-frequency event listeners (scroll, resize, search input).
   - Offload heavy compute (data parsing, encryption, image manipulation) to Web Workers.
3. **CLS (Cumulative Layout Shift <= 0.1)**:
   - Always specify explicit `width` and `height` or CSS `aspect-ratio` on all `<img>`, `<video>`, and embeds.
   - Reserve skeleton or container space for dynamic content, banners, and asynchronous widgets.
   - Never inject dynamic content above existing content unless triggered by direct user action.
</CORE_WEB_VITALS>

<BUNDLE_HYGIENE>
1. **Tree-Shaking**:
   - Ban barrel imports that pull entire libraries (e.g. `import { debounce } from 'lodash'`). Use path imports (`import debounce from 'lodash/debounce'`) or native platform methods.
2. **Code-Splitting**:
   - Lazy load heavy modules, chart libraries, and interactive modals via dynamic `import()` or `React.lazy()`.
   - Route-based chunking: Ensure landing pages do not bundle admin dashboard code.
</BUNDLE_HYGIENE>

<PROCEDURAL_WORKFLOW>
1. **Audit**: Identify rendering bottlenecks, large imports, and missing image dimensions.
2. **Apply Minimal Targeted Fixes**: Modify only the bottlenecks without breaking API contracts.
3. **Verify**: Run `python3 scripts/verify.py --execute` and ensure zero layout or functional regressions.
</PROCEDURAL_WORKFLOW>
