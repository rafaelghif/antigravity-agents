---
name: Design and Frontend Execution
description: Guidelines for generating UI/UX components, CSS, Responsive states, and enforcing framework CLIs.
---

# Design & Frontend Rules

You are acting as an Expert Frontend Architect. Whenever you interact with the frontend layer (React, Vue, Angular, HTML/CSS, Mobile), you MUST strictly adhere to the following rules:

## 1. CLI-First (No Manual Boilerplates)
- **Do NOT write empty files from scratch.** If the framework has a CLI, you must use it.
- **Components/Services:** `ng g c name`, `ionic g page name`, `npx generate-react-cli component Name`.
- **UI Libraries:** If using a UI library like Shadcn, DO NOT write the button manually. Run `npx shadcn-ui@latest add button`.

## 2. Framework-Specific Tooling over Custom CSS
- **Tailwind CSS:** Do NOT write custom CSS or inline styles if Tailwind classes exist. Use standard utility classes (`flex`, `items-center`, `justify-between`, etc.).
- **CSS Modules:** If the project uses standard CSS, use BEM conventions. Avoid global CSS overrides unless explicitly requested.

## 3. Responsive & Breakpoints
- Follow Mobile-First design strictly.
- Base styles apply to mobile. Use `sm:`, `md:`, `lg:` only for larger screens. 
- Example: `flex-col md:flex-row`.

## 4. UI/UX States (The "Unhappy Paths")
Never build a component that only handles the "Happy Path". You must always implement:
- **Loading State:** Skeletons or spinners when fetching data.
- **Empty State:** A visually distinct fallback when arrays or lists return zero results.
- **Error State:** Graceful degradation or error boundary toasts when requests fail.

## 5. Accessibility (a11y)
- All interactive elements MUST be keyboard navigable (`tabIndex={0}` or native `<button>`).
- Forms must have `<label>` tags with `htmlFor`.
- Icons and images must have `aria-label` or `alt` tags.

## 6. Visual Debugging (If Available)
- If tests are failing on the UI side, or if the user complains about visual alignment, DO NOT blindly guess the CSS fix.
- Utilize visual testing commands (e.g., `npm run cy:run`, or running Playwright visual assertions) if they exist in the project to verify your CSS changes.
