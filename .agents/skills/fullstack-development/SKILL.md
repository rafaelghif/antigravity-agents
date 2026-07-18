---
name: fullstack-development
description: Framework-agnostic principles for building scalable web applications, focusing on clean API boundaries, reusable components, and efficient state management.
---

# Fullstack Development Standards

This playbook defines framework-agnostic architectural standards for building scalable, maintainable, and high-performance fullstack web applications. These principles apply regardless of the specific technology stack (e.g., React/Node, Next.js, Go/HTMX, Vue/Laravel).

## 1. Clean API Boundaries & Separation of Concerns
* **Decoupled Layers:** Frontend clients and backend services must be strictly decoupled. Communicate exclusively via defined, versioned API contracts (REST, GraphQL, or RPC).
* **Business Logic Isolation:** Keep business logic out of UI components and routing layers. Centralize it in dedicated service modules or controllers.
* **Stateless Backends:** API endpoints should be stateless where possible to allow horizontal scaling. Use tokens (JWT) or distributed session stores for authentication.

## 2. Reusable Component Architecture
* **Dumb vs. Smart Components:** Strictly separate presentation (dumb) components from container (smart/data-fetching) components. 
* **Composition over Inheritance:** Build complex UIs by composing small, highly cohesive, single-purpose components.
* **Prop Drilling Avoidance:** Use appropriate context or state management libraries instead of passing props down deeply nested component trees.

## 3. Efficient State Management
* **Server vs. Client State:** Clearly distinguish between server state (data fetched from DB/API) and client state (UI toggles, themes, unsubmitted forms). 
* **Data Fetching:** Use modern data-fetching paradigms (e.g., SWR, React Query, or SSR fetching) that provide built-in caching, revalidation, and loading state management.
* **Mutation Optimization:** Implement optimistic UI updates for mutations to ensure the application feels instantly responsive to user actions.

## 4. Implementation Checklist
* [ ] Is the frontend completely decoupled from the backend's internal logic?
* [ ] Are UI components modular, reusable, and free of direct API calls?
* [ ] Is server state cached and managed efficiently without redundant network requests?
* [ ] Are optimistic updates implemented for critical data mutations?
* [ ] Are errors and loading states handled gracefully at the component level?
