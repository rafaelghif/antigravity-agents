#!/usr/bin/env bash
# Antigravity Agent Core - Autonomous Reconnaissance Script
# Scans the target workspace to automatically configure the agent environment blueprints.

set -euo pipefail

# Parse arguments
FORCE_OVERWRITE=false
while [ $# -gt 0 ]; do
    case "$1" in
        -f|--force)
            FORCE_OVERWRITE=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Helper function to write templates safely (preserves existing files unless -f/--force is specified)
write_recon_file_safe() {
    local target_file="$1"
    if [ -f "$target_file" ] && [ "$FORCE_OVERWRITE" = "false" ]; then
        echo "  [PRESERVE] $target_file already exists. Preserving current file."
    else
        echo "  [WRITE] Writing $target_file..."
        cat > "$target_file"
    fi
}

PROJECT_RULES_FILE=".agents/project_rules.md"
SCHEMA_INDEX_FILE=".agents/schema.md"
SCHEMAS_DIR=".agents/schemas"

echo "=========================================================="
echo "Running Autonomous Codebase Reconnaissance..."
echo "=========================================================="

# 1. Tech Stack Detection
TECH_STACK="Unknown"
BUILD_CMD="echo 'No build command needed'"
TEST_CMD="echo 'No test suite found'"
LINT_CMD="echo 'No linter found'"
ARCH_PATTERN="Standard Model-View-Controller (MVC)"

IS_MONOREPO=false
SUBPROJECTS_FILE=".agents/subprojects.sh"
rm -f "$SUBPROJECTS_FILE"

# Detect if monorepo
if [ -f pnpm-workspace.yaml ] || [ -f turbo.json ] || [ -f lerna.json ] || [ -f go.work ] || ( [ -f package.json ] && grep -q '"workspaces"' package.json ) || ( [ -f Cargo.toml ] && grep -q "\[workspace\]" Cargo.toml ); then
    IS_MONOREPO=true
fi

if [ "$IS_MONOREPO" = "true" ]; then
    TECH_STACK="Monorepo"
    ARCH_PATTERN="Decoupled / Distributed Architecture"
    BUILD_CMD="./.agents/scripts/helper.sh build"
    TEST_CMD="./.agents/scripts/helper.sh test"
    LINT_CMD="./.agents/scripts/helper.sh lint"
    
    # Discovery loop
    discovered_projects=""
    declare -a sp_list=()
    NL=$'\n'
    
    # Find all sub-directories under apps/, packages/, services/ up to 1 level deep
    for dir in apps/* packages/* services/*; do
        if [ -d "$dir" ]; then
            # Signature check in sub-directory
            sub_stack="Unknown"
            sub_build="echo 'No build command'"
            sub_test="echo 'No test command'"
            sub_lint="echo 'No lint command'"
            
            if [ -f "$dir/package.json" ]; then
                sub_stack="Node.js"
                if grep -q '"typescript"' "$dir/package.json"; then sub_stack="Node.js (TypeScript)"; fi
                if grep -q '"next"' "$dir/package.json"; then sub_stack="Next.js"; fi
                if grep -q '"build"' "$dir/package.json"; then sub_build="npm run build"; else sub_build="echo 'No build step'"; fi
                if grep -q '"test"' "$dir/package.json"; then sub_test="npm run test"; fi
                if grep -q '"lint"' "$dir/package.json"; then sub_lint="npm run lint"; fi
            elif [ -f "$dir/go.mod" ]; then
                sub_stack="Go"
                sub_build="go build -o bin/server src/cmd/server/main.go 2>/dev/null || go build ./..."
                sub_test="go test ./..."
                sub_lint="golangci-lint run ./..."
                if [ -f "$dir/Makefile" ]; then
                    sub_build="make build"
                    sub_test="make test"
                fi
            elif [ -f "$dir/requirements.txt" ] || [ -f "$dir/pyproject.toml" ]; then
                sub_stack="Python"
                sub_build="echo 'No build step'"
                if grep -q "fastapi" "$dir/requirements.txt" 2>/dev/null || grep -q "fastapi" "$dir/pyproject.toml" 2>/dev/null; then
                    sub_stack="Python (FastAPI)"
                fi
                if grep -q "pytest" "$dir/requirements.txt" 2>/dev/null || grep -q "pytest" "$dir/pyproject.toml" 2>/dev/null; then
                    sub_test="pytest"
                else
                    sub_test="python -m unittest discover"
                fi
                sub_lint="flake8 . || black --check ."
            fi
            
            if [ "$sub_stack" != "Unknown" ]; then
                sp_list+=("$dir|$sub_stack|$sub_build|$sub_test|$sub_lint")
                discovered_projects="${discovered_projects}${NL}  - \`$dir/\` -> $sub_stack"
            fi
        fi
    done
    
    # Save the subprojects configuration file
    if [ ${#sp_list[@]} -gt 0 ]; then
        echo "SUBPROJECTS=(" > "$SUBPROJECTS_FILE"
        for sp in "${sp_list[@]}"; do
            echo "  \"$sp\"" >> "$SUBPROJECTS_FILE"
        done
        echo ")" >> "$SUBPROJECTS_FILE"
    fi
else
    if [ -f package.json ]; then
        TECH_STACK="Node.js"
        if grep -q '"typescript"' package.json; then
            TECH_STACK="Node.js (TypeScript)"
        fi
        if grep -q '"next"' package.json; then
            TECH_STACK="Next.js / React"
            ARCH_PATTERN="Next.js App Router Architecture"
        elif grep -q '"nest"' package.json; then
            TECH_STACK="NestJS (TypeScript)"
            ARCH_PATTERN="Modular NestJS Dependency Injection Architecture"
        elif grep -q '"react"' package.json; then
            TECH_STACK="React SPA"
            ARCH_PATTERN="Component-Driven SPA Architecture"
        elif grep -q '"express"' package.json; then
            TECH_STACK="Express API"
            ARCH_PATTERN="Express Layered Routing Architecture"
        fi
        
        # Extract package.json scripts
        if grep -q '"build"' package.json; then BUILD_CMD="npm run build"; fi
        if grep -q '"test"' package.json; then TEST_CMD="npm run test"; fi
        if grep -q '"lint"' package.json; then LINT_CMD="npm run lint"; fi
    elif [ -f go.mod ]; then
        TECH_STACK="Go"
        module_name=$(grep "^module " go.mod | cut -d' ' -f2 || echo "project")
        TECH_STACK="Go Module: $module_name"
        ARCH_PATTERN="Hexagonal / Domain-Driven Design in Go"
        BUILD_CMD="go build ./..."
        TEST_CMD="go test ./..."
        LINT_CMD="golangci-lint run"
        if grep -q "gin-gonic/gin" go.mod; then
            TECH_STACK="Go (Gin)"
            ARCH_PATTERN="Clean Architecture REST API"
            if [ -f Makefile ]; then
                BUILD_CMD="make build"
                TEST_CMD="make test"
            else
                BUILD_CMD="go build -o bin/server src/cmd/server/main.go"
                TEST_CMD="go test -v ./tests/..."
            fi
        fi
    elif [ -f Cargo.toml ]; then
        TECH_STACK="Rust"
        ARCH_PATTERN="Modular Cargo Workspace Architecture"
        BUILD_CMD="cargo build"
        TEST_CMD="cargo test"
        LINT_CMD="cargo clippy"
    elif [ -f requirements.txt ] || [ -f pyproject.toml ] || [ -f Pipfile ]; then
        TECH_STACK="Python"
        BUILD_CMD="echo 'No build step required'"
        
        if [ -f pyproject.toml ] && grep -q "fastapi" pyproject.toml; then
            TECH_STACK="Python (FastAPI)"
            ARCH_PATTERN="Asynchronous layered API structure"
        elif [ -f requirements.txt ] && grep -q "fastapi" requirements.txt; then
            TECH_STACK="Python (FastAPI)"
            ARCH_PATTERN="Asynchronous layered API structure"
        elif [ -f requirements.txt ] && grep -q "django" requirements.txt; then
            TECH_STACK="Python (Django)"
            ARCH_PATTERN="Django MTV Pattern"
        fi

        if [ -f requirements.txt ] && grep -q "pytest" requirements.txt; then
            TEST_CMD="pytest"
        else
            TEST_CMD="python -m unittest discover"
        fi
        LINT_CMD="flake8 . || black --check ."
    elif [ -f composer.json ]; then
        TECH_STACK="PHP"
        if grep -q '"laravel/framework"' composer.json; then
            TECH_STACK="PHP (Laravel)"
            ARCH_PATTERN="Laravel MVC / Eloquent Architecture"
        fi
        BUILD_CMD="composer install"
        TEST_CMD="vendor/bin/phpunit"
        LINT_CMD="vendor/bin/php-cs-fixer fix --dry-run"
    elif [ -f Gemfile ]; then
        TECH_STACK="Ruby"
        if grep -q "rails" Gemfile; then
            TECH_STACK="Ruby on Rails"
            ARCH_PATTERN="Rails Convention-over-Configuration MVC"
        fi
        BUILD_CMD="bundle install"
        TEST_CMD="bundle exec rake test"
        LINT_CMD="bundle exec rubocop"
    fi
fi

echo "Detected Stack: $TECH_STACK"
echo "Detected Build: $BUILD_CMD"
echo "Detected Test:  $TEST_CMD"
echo "Detected Lint:  $LINT_CMD"

# 2. Directory Structure Mapping
NL=$'\n'
DIRS=""
if [ "$IS_MONOREPO" = "true" ]; then
    DIRS="$discovered_projects"
else
    for d in src lib app apps controllers views handlers models services repositories routes tests test config pkg cmd; do
        if [ -d "$d" ]; then
            DIRS="${DIRS}${NL}  - \`$d/\` -> Project workspace component"
        fi
    done
fi

if [ -z "$DIRS" ]; then
    DIRS="${NL}  - Root directory contains project files."
fi

# 3. Database & ORM Detection
DB_STACK="None detected"
if [ -f prisma/schema.prisma ]; then
    DB_STACK="Prisma ORM (schema: prisma/schema.prisma)"
elif grep -r -q "sequelize" package.json 2>/dev/null || [ -d models ] && grep -r -q "Sequelize" models/ 2>/dev/null; then
    DB_STACK="Sequelize ORM"
elif grep -r -q "typeorm" package.json 2>/dev/null; then
    DB_STACK="TypeORM"
elif grep -r -q "sqlalchemy" requirements.txt pyproject.toml 2>/dev/null; then
    DB_STACK="SQLAlchemy ORM"
elif grep -r -q "gorm.io" go.mod 2>/dev/null; then
    DB_STACK="GORM (Go)"
elif [ -d db/migrate ]; then
    DB_STACK="Rails ActiveRecord Migrations"
elif [ -d database/migrations ]; then
    DB_STACK="Laravel Eloquent Migrations"
fi

echo "Detected Database/ORM: $DB_STACK"

# 4. Environment Template Variable Extraction
ENV_VARS=""
if [ -f .env.example ]; then
    ENV_VARS=$(grep -v '^#' .env.example | grep '=' | cut -d'=' -f1 | sed 's/^/  - /' || true)
elif [ -f .env ]; then
    ENV_VARS=$(grep -v '^#' .env | grep '=' | cut -d'=' -f1 | sed 's/^/  - /' || true)
fi

if [ -z "$ENV_VARS" ]; then
    ENV_VARS="  - No configuration parameters detected."
fi

# 5. Populate .agents/project_rules.md
write_recon_file_safe "$PROJECT_RULES_FILE" << PAB_EOF
# Project Architecture Blueprint (PAB)

This file defines the specific technical stack, directory boundaries, coding standards, and system dependencies for this project.

---

## 1. Stack & Directory Boundaries
- **Primary Language/Framework**: $TECH_STACK
- **Directory Structure**:$DIRS

## 2. Architectural Conventions
- **Architectural Pattern**: $ARCH_PATTERN
- **Boundary insulation**: Core domain logic must remain completely independent of external libraries, databases, and frameworks.

## 3. Spacing & Styling Standards
- **Linter command**: \`$LINT_CMD\`
- **Build validation**: \`$BUILD_CMD\`
- **Test runner command**: \`$TEST_CMD\`
- **Follow formatting**: Follow standard formatting guidelines for $TECH_STACK development.

## 4. Security & External Services
- **Database/ORM**: $DB_STACK
- **Required Configuration Variables**:
$ENV_VARS

## 5. Long-Term Impact & 10-Year Maintainability Gates
- **Impact-Analysis Check**: Before installing new packages, modifying database structures, or altering cross-domain APIs, the agent must run the \`impact-analysis\` skill and document design rationales.
- **Architectural Boundary Gate**: Domain business logic must remain completely independent of libraries and frameworks (e.g. database schemas, server frameworks).
- **Code Sustainability**: Code must prioritize long-term readability over brevity. Avoid complex runtime assumptions, unverified imports, or undocumented configuration requirements.
- **Ambiguity Gate**: If any implementation details are unclear, halt and ask the user for confirmation first.

## 6. Multi-Agent & Teamwork Constraints
- **Autonomous Bootstrapping Sequence**: Before performing any edit or script action, you MUST read the core files in sequence: \`AGENTS.md\`, \`.agents/project_rules.md\`, \`.agents/schema.md\`, and \`.agents/memory.md\`. No file writes or terminal runs are allowed prior to this initialization.
- **Workspace Git Tracking**: Never ignore \`.agents/\` or \`AGENTS.md\` in \`.gitignore\` (except \`.agents/locks/\`). Commit all memory, schemas, dynamic workflows, and ADR files to Git to ensure proper multi-agent synchronization.
- **Upstream Sync Gate**: You must run \`./.agents/scripts/helper.sh validate\` before beginning code changes to check if the branch is behind origin. If it is behind, stop and ask the user to pull first.
- **Discussion and Design Plans**: Document all \`/grill-me\` outcomes and execution plans under \`.agents/workflows/task_<task_name>.md\`. Never log task-specific plans or checklists globally or in the main memory ledger.
- **Real-Time Schema & Dependency Updates**: Any discussion on database models, API routes, or third-party libraries must be documented in the repository *immediately* before starting code edits:
  - Database structures must be saved under \`.agents/schemas/\` and registered in \`.agents/schema.md\`.
  - Technologies/libraries must be documented in \`.agents/project_rules.md\` and their respective workspace configuration files (\`package.json\`, \`go.mod\`, etc.).
  - Architectural decisions must be documented as a new ADR entry in \`.agents/adr.md\`.
- **Strict Checklist Checkbox Rules**: Checklists must follow a strict 3-state lifecycle. Only ONE task can be marked \`[/]\` at a time across the entire workspace. Do not change a task checklist state to \`[x]\` until verification has passed and the changes have been staged and committed in the completed state.
- **Handover Relayed Context**: Before logging off or ending a turn, you MUST write concise handover notes (under 5 lines) in the active memory ledger under \`## 3. Relayed Context & Handover Notes\`. This ensures any incoming agent or new account knows exactly where to resume work without token waste.
PAB_EOF

# 6. Database schema domain mapping (Auto-discover domain tables or modules)
mkdir -p "$SCHEMAS_DIR"

# Write a basic schema.md index file
if [ "$DB_STACK" = "Prisma ORM (schema: prisma/schema.prisma)" ]; then
    write_recon_file_safe "$SCHEMA_INDEX_FILE" << SRD_EOF
# Technical Schema & Reference Database (SRD) - Index Map

This file serves as the high-level index for the project's technical schemas, database specifications, and API contracts.

---

## 1. Domain Schemas Index
- [Default Module](file://./schemas/default_module.md) -> Reference: [default_module.md](file://./schemas/default_module.md)
- [Database Schema (Prisma)](file://./schemas/database_schema.md) -> Reference: [database_schema.md](file://./schemas/database_schema.md)
SRD_EOF
else
    write_recon_file_safe "$SCHEMA_INDEX_FILE" << SRD_EOF
# Technical Schema & Reference Database (SRD) - Index Map

This file serves as the high-level index for the project's technical schemas, database specifications, and API contracts.

---

## 1. Domain Schemas Index
- [Default Module](file://./schemas/default_module.md) -> Reference: [default_module.md](file://./schemas/default_module.md)
SRD_EOF
fi

# Check for custom schema files
if [ "$DB_STACK" = "Prisma ORM (schema: prisma/schema.prisma)" ]; then
    # Create prisma schema domain layout
    write_recon_file_safe "$SCHEMAS_DIR/database_schema.md" << PRISMA_EOF
# Schema: Database Models (Prisma)

Automatically discovered Prisma model entities:

---

## 1. Relational Database Tables / Models
$(grep -E "^model " prisma/schema.prisma | cut -d' ' -f2 | sed 's/^/- /' || true)
PRISMA_EOF
fi

echo "=========================================================="
echo "Reconnaissance Complete! Blueprints updated successfully."
echo "=========================================================="
