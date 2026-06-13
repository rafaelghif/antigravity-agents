---
name: mvc-conventions
activation: Model Decision

description: "Conventions for standard Model-View-Controller (MVC) architecture and boundary insulation."
---

# mvc-conventions Workspace Rule

## Guidelines
- **Architectural Pattern**: Standard Model-View-Controller (MVC)
- **Boundary insulation**: Core domain logic must remain completely independent of external libraries, databases, and frameworks.
- **Pure business logic**: Insulate core services (`src/services/`) from HTTP requests (controllers) or database direct concerns (models/TypeORM).
