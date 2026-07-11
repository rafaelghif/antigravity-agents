# Model-View-Controller (MVC) Architecture Blueprint

This blueprint outlines standard practices for separating applications into Model, View, and Controller layers to isolate data access, presentation, and user input orchestration.

## 1. Directory Structure

```
src/
├── models/                  # Data objects, schemas, database wrappers, and core algorithms
│   ├── user.py
│   └── post.py
├── views/                   # Presentation templates or output formatters (HTML, JSON, etc.)
│   ├── templates/
│   │   ├── index.html
│   │   └── profile.html
│   └── formatters.py
└── controllers/             # Validates inputs, handles requests, calls models, and serves views
    ├── auth_controller.py
    └── post_controller.py
```

## 2. Architectural Guidelines

* **Model**: Represents the application state and data access. It should have zero knowledge of view templates or HTTP requests.
* **View**: Formats and renders data from the model. It should remain passive, without logic to mutate data or parse requests.
* **Controller**: The entry point for requests. It queries/updates the model and passes the resulting data to the view for presentation.

## 3. Implementation Checklist

- [ ] HTTP-specific dependencies (request objects, session variables) are kept inside the `controller` layer, never bleeding into the `model`.
- [ ] Views do not run database queries; they only receive pre-fetched data from the controller.
- [ ] Database queries and updates are encapsulated inside model classes or repositories.
