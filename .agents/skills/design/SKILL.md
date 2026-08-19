---
name: design
description: Use this skill when the user asks to modify or create UI components, apply CSS styling, manage frontend architectures, or debug visual issues.
---

<CRITICAL_DIRECTIVE>
Enforce expert-level Frontend Architecture and strict design consistency during implementation.
</CRITICAL_DIRECTIVE>

<ENTERPRISE_STANDARDS>
1. **CLI-First**: DO NOT write boilerplate manually. You MUST use native framework CLIs (e.g., `nest g`, `ionic g page`, `npx shadcn-ui add`) for structural generation.
2. **Framework Tooling**: Strictly use utility classes (e.g., Tailwind CSS) or standard module scoping. Ban custom global CSS overrides unless explicitly required.
3. **Responsive Design**: Follow Mobile-First design strictly. Base styles apply to mobile; use `sm:`, `md:`, `lg:` exclusively for larger viewports.
4. **State Management**: Every component MUST account for "Unhappy Paths": Loading states (Skeletons/Spinners), Empty states (visual fallbacks), and Error states (graceful degradation/toasts).
5. **Accessibility (a11y)**: All interactive elements MUST be keyboard navigable. Mandate the use of semantic HTML, ARIA labels, and explicit form associations.
</ENTERPRISE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Design Context Acquisition**: Identify the project's styling framework before writing code to prevent framework collision.
2. **Component Scaffold**: Run the corresponding framework CLI tool to scaffold the requested component.
3. **Implementation**: Edit the scaffolded file and strictly apply the `ENTERPRISE_STANDARDS`.
4. **Visual Testing**: If visual regression or integration testing tools exist, use them to verify your implementation.
5. **Diff Review**: Inspect your diff to ensure no hardcoded colors, missing accessibility attributes, or forgotten empty/error states remain.
</PROCEDURAL_WORKFLOW>
