---
name: design
description: Use this skill when the user asks to modify or create UI components, apply CSS styling, manage frontend architectures, or debug visual issues.
---

<CRITICAL_DIRECTIVE>
Enforce expert-level Frontend Architecture and strict design consistency during implementation.
</CRITICAL_DIRECTIVE>

<ENTERPRISE_STANDARDS>
1. **Design System & Component SSOT (Strict DRY)**: MUST reuse existing project UI components (`Button`, `Card`, `Input`, `Dialog`, `Table`). Strictly FORBID writing one-off ad-hoc styled HTML elements across different pages.
2. **Frontend Pattern Harmony**: Maintain 100% consistency across pages for state management (e.g. Zustand, TanStack Query), data-fetching hooks, error boundaries, and toast notifications.
3. **CLI-First Scaffolding**: Use native framework CLIs (e.g. `npx shadcn-ui add`, `nest g`, `ionic g page`) for component generation rather than writing raw boilerplate.
4. **Utility & Theming Consistency**: Strictly use the project's styling utility (e.g. Tailwind classes with `cn()` merge utility). Ban conflicting inline styles or arbitrary hardcoded color hex codes.
5. **Mobile-First Responsive Design**: Base styles apply to mobile; use `sm:`, `md:`, `lg:` exclusively for larger viewports. No fragile absolute positioning hacks.
6. **Complete State Spectrum**: Every view MUST account for the full lifecycle: Loading states (Skeletons/Shimmers), Empty states (visual fallbacks + CTAs), Error states (toast/banner with retry), and Success states.
7. **Accessibility (a11y)**: All interactive elements MUST be keyboard navigable. Mandate semantic HTML, ARIA attributes, explicit label associations, and WCAG AA contrast.
</ENTERPRISE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Design System Discovery**: Search for existing UI component libraries and styling patterns in the project (`grep_search` in `components/`, `ui/`, `hooks/`).
2. **Component Reuse Check**: Audit if existing primitives or hooks can satisfy the requirement before creating new files.
3. **Scaffold & Implement**: Use CLI where appropriate and implement adhering strictly to `ENTERPRISE_STANDARDS`.
4. **Visual & Interaction Verification**: Verify responsiveness, keyboard navigation, and loading/empty/error states.
5. **Diff Review**: Inspect diff for zero hardcoded styles, zero duplicated UI primitives, and 100% a11y compliance.
</PROCEDURAL_WORKFLOW>


<L9_STANDARDS>
- **Component Reusability**: Extract repetitive UI into atomic components.
- **Responsive First**: Mobile-first CSS. No absolute positioning hacks.
- **Accessibility (a11y)**: Aria labels, contrast ratios, and keyboard navigation are non-negotiable.
</L9_STANDARDS>
