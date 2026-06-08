---
name: infra-provisioner
description: Generates, configures, and orchestrates local Docker and Docker Compose environments for system dependencies like databases, caches, and object storage.
---

# Infrastructure Provisioner Skill

## 1. Input Specification
- **Environment Configuration**: A `.env` file containing credentials (e.g., database user, cache credentials, API endpoints).
- **Network Boundaries**: Bridged private network configurations for cross-container communication.

## 2. Operational Procedures & Checklist
1. **Compose File Construction**:
   - Write a `docker-compose.yml` at the repository root.
   - Set up standard containers based on project dependencies (e.g. database, cache, storage).
   - Configure named persistent volumes to preserve service state.
2. **Resource Constraints**:
   - Restrict memory and CPU usage per service in local development environments to prevent host resource exhaustion.
3. **Decoupled Healthchecks**:
   - Configure health checks to verify that each service is fully operational.
   - Define interval, timeout, retries, and start period windows.
4. **Service Startup Sequencing**:
   - Map dependencies explicitly using `depends_on` with the `condition: service_healthy` clause to ensure services boot in the correct order.
5. **Autoprovisioning Scripts**:
   - Set up auto-initialization scripts or containers (e.g., creating database tables, seeding mock data, setting up default storage buckets).

## 3. Decision Matrix
- **Is a required service already running on the host system?**
   - **YES**: Do **NOT** shut down host processes. Edit the port binding in the local container configuration (e.g., bind host port `5433` to container port `5432`) and update environment configs.
- **Do logs indicate initialization failures due to invalid credentials or volumes?**
   - **YES**: Stop container, purge invalid volumes (`docker compose down -v`), correct configuration values, and restart services.

## 4. Error Mitigation Tree
- **Container health check times out or fails**:
   - *Mitigation*: Run `docker compose logs <service-name>` to identify error logs. Common fixes include adjusting database permissions, increasing the health check `start_period`, or correcting credential mismatches.
- **Docker daemon is unresponsive**:
   - *Mitigation*: Run `docker info` to verify state. Prompt the user to ensure Docker is running.

## 5. Output Verification Gate
- Run validation check: `docker compose ps`. Verify all services are listed as healthy.
- Connect to database and cache dependencies to verify credentials.
- Record local infrastructure status in the active memory ledger (`.agents/memory.md`).
