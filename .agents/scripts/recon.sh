#!/usr/bin/env bash
# Antigravity Agent Core - Autonomous Reconnaissance Script
# Scans the target workspace to automatically configure the agent environment blueprints.

set -euo pipefail

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
    local module_name
    module_name=$(grep "^module " go.mod | cut -d' ' -f2)
    TECH_STACK="Go Module: $module_name"
    ARCH_PATTERN="Hexagonal / Domain-Driven Design in Go"
    BUILD_CMD="go build ./..."
    TEST_CMD="go test ./..."
    LINT_CMD="golangci-lint run"
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

echo "Detected Stack: $TECH_STACK"
echo "Detected Build: $BUILD_CMD"
echo "Detected Test:  $TEST_CMD"
echo "Detected Lint:  $LINT_CMD"

# 2. Directory Structure Mapping
NL=$'\n'
DIRS=""
for d in src lib app apps controllers views handlers models services repositories routes tests test config pkg cmd; do
    if [ -d "$d" ]; then
        DIRS="${DIRS}${NL}  - \`$d/\` -> Project workspace component"
    fi
done

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
cat << PAB_EOF > "$PROJECT_RULES_FILE"
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
PAB_EOF

# 6. Database schema domain mapping (Auto-discover domain tables or modules)
mkdir -p "$SCHEMAS_DIR"

# Write a basic schema.md index file
cat << SRD_EOF > "$SCHEMA_INDEX_FILE"
# Technical Schema & Reference Database (SRD) - Index Map

This file serves as the high-level index for the project's technical schemas, database specifications, and API contracts.

---

## 1. Domain Schemas Index
- [Default Module](file://./schemas/default_module.md) -> Reference: [default_module.md](file://./schemas/default_module.md)
SRD_EOF

# Check for custom schema files
if [ "$DB_STACK" = "Prisma ORM (schema: prisma/schema.prisma)" ]; then
    # Create prisma schema domain layout
    cat << PRISMA_EOF > "$SCHEMAS_DIR/database_schema.md"
# Schema: Database Models (Prisma)

Automatically discovered Prisma model entities:

---

## 1. Relational Database Tables / Models
$(grep -E "^model " prisma/schema.prisma | cut -d' ' -f2 | sed 's/^/- /' || true)
PRISMA_EOF

    cat << SRD_EOF >> "$SCHEMA_INDEX_FILE"
- [Database Schema (Prisma)](file://./schemas/database_schema.md) -> Reference: [database_schema.md](file://./schemas/database_schema.md)
SRD_EOF
fi

echo "=========================================================="
echo "Reconnaissance Complete! Blueprints updated successfully."
echo "=========================================================="
