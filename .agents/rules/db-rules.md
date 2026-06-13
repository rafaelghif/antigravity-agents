---
name: db-rules
activation: Glob
pattern: "src/models/**/*.ts"

---

# db-rules Workspace Rule

## Guidelines
- **Database/ORM**: TypeORM
- **Entities & Tables**:
  - Keep database model/entity classes under `src/models/`.
  - Ensure entity mappings use decorators cleanly and define proper relations (e.g. `@Entity()`, `@Column()`, `@ManyToOne()`).
- **Purity Gate**:
  - Never run raw DB queries directly inside controllers or services. Always encapsulate db operations inside repositories or model wrappers.
