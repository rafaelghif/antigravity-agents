---
name: ui-ux-design
description: Strict guidelines enforcing modern UI aesthetics (Glassmorphism, Dark-mode first), micro-animations, Accessibility (a11y), and Core Web Vitals optimization.
---

# UI/UX Design & Aesthetic Standards

This playbook defines the strict aesthetic and user experience standards required for any frontend development. The goal is to completely avoid "generic AI" outputs by enforcing high-end, professional, and bespoke design patterns.

## 1. Aesthetic Principles
* **Anti-Generic Design:** Do NOT use default, unstyled, or raw component libraries (e.g., raw Bootstrap, default Tailwind without curation). Designs must feel bespoke, polished, and tailored.
* **Modern Paradigms:** 
  * **Dark-Mode First:** Prioritize dark mode designs with high contrast ratios, refined typography (e.g., Inter, Roboto, Outfit), and subtle glowing effects.
  * **Glassmorphism:** Utilize frosted glass effects (`backdrop-blur`), subtle translucent borders, and soft gradients.
  * **Micro-Animations:** Implement smooth hover states, layout transitions, and loading states. Interfaces must feel alive and highly responsive (avoid instant, rigid state jumps).

## 2. Accessibility (a11y) & UX
* **Semantic HTML:** Always use correct HTML5 elements (`<nav>`, `<main>`, `<article>`, `<button>` vs `<a>`) for screen reader compatibility.
* **Contrast & Legibility:** Maintain WCAG 2.1 AA compliance for text contrast. Ensure focus rings are visible for keyboard navigation.
* **Aria Attributes:** Implement standard `aria-*` labels for dynamic or custom interactive elements.

## 3. Core Web Vitals (Performance)
* **LCP (Largest Contentful Paint):** Preload hero images/fonts. Defer offscreen loading.
* **FID (First Input Delay):** Minimize main-thread blocking JavaScript. Keep interactions snappy.
* **CLS (Cumulative Layout Shift):** Always reserve space for images, ads, and dynamic content to prevent layout jumps during load.

## 4. Implementation Checklist
* [ ] Does the UI look premium (not like a generic template)?
* [ ] Are micro-animations applied to interactive elements?
* [ ] Is it fully responsive across mobile, tablet, and desktop?
* [ ] Are Core Web Vitals considered in the DOM structure?
* [ ] Is the design fully accessible (keyboard navigation, semantic tags, contrast)?
