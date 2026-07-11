# Atomic Component Design Blueprint

This blueprint outlines standard practices for organizing user interface components hierarchically using the principles of Atomic Design (Atoms, Molecules, Organisms, Templates, Pages).

## 1. Directory Structure

```
src/
└── presentation/
    └── components/
        ├── atoms/           # Basic, indivisible HTML/CSS building blocks (no business logic)
        │   ├── Button.js
        │   └── Input.js
        ├── molecules/       # Combinations of atoms that function together as a unit
        │   ├── SearchBar.js # (Input atom + Button atom)
        │   └── FormField.js
        ├── organisms/       # Complex UI components composed of molecules and atoms
        │   ├── Header.js
        │   └── ProductGrid.js
        ├── templates/       # Layouts structuring components on the page (no concrete content)
        │   └── DashboardLayout.js
        └── pages/           # Concrete views that map templates to API data and state
            └── Dashboard.js
```

## 2. Boundary & Dependency Rules

* **Atoms** must never import other components. They are styled elements receiving props.
* **Molecules** can only import atoms. They do not import organisms, templates, or pages.
* **Organisms** can import molecules and atoms. They manage complex interactions but avoid direct routing couplings.
* **Templates** focus on grid and slot layout. They do not contain hardcoded textual copy or domain-specific fetching.
* **Pages** handle routing, context bindings, and API fetching, passing state down to templates and organisms.

## 3. Implementation Checklist

- [ ] Atoms have zero external API fetching logic and zero global state dependencies.
- [ ] Custom hooks are decoupled and kept at the page or organism level.
- [ ] Layout slots/children props are utilized in templates to preserve generic structuring.
