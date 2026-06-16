#!/usr/bin/env bash
# Antigravity Agent Core Helper Script
set -euo pipefail

MEMORY_FILE=".agents/memory.md"
LOCKS_DIR=".agents/locks"
ARCHIVE_DIR=".agents/archive"

show_help() {
    echo "=========================================================="
    echo "            Antigravity Agent Command-Line Helper"
    echo "=========================================================="
    echo "Usage: \$0 [command] [args]"
    echo ""
    echo "Daily Developer Commands:"
    echo "  init              Start scaffolding wizard (interactive or with arguments)"
    echo "  doctor            Diagnose workspace health and check active locks"
    echo "  lock <module>     Lock a directory module to prevent parallel edits"
    echo "  unlock <module>   Unlock a directory module"
    echo "  commit            Run tests, rotate profiles, and create Conventional Commit"
    echo "  git-profile       Switch Git configurations locally (use 'rotate' to rotate)"
    echo "  api-profile       Switch API configurations locally (use 'rotate' to rotate)"
    echo ""
    echo "Rules & Skill Extending Commands:"
    echo "  create-skill      Scaffold a new specialized skill directory"
    echo "  list-skills       Audit all registered skills for compliance"
    echo "  create-rule       Scaffold a new workspace rule file under .agents/rules/"
    echo "  list-rules        Audit all workspace rules for compliance"
    echo "  create-adr        Scaffold a new Architectural Decision Record"
    echo "  release           Auto-increment version and update CHANGELOG.md"
    echo ""
    echo "Automated & CI/CD Commands:"
    echo "  validate          Audit secrets, memory limits, and domain isolation"
    echo "  recon             Run stack auto-detection and regenerate blueprints"
    echo "  sync-git          Synchronize active branch/commit with memory.md"
    echo "  archive           Archive completed checklists before PR merges"
    echo "  migrate           Upgrade older workspaces to current version format"
    echo "  build/lint/test   Monorepo-aware builder, linter, and testing runners"
    echo "  sync-api          Generate a typed TypeScript client from backend API"
    echo "  log-usage         Log token usage stats to token_budget.json"
    echo ""
    echo "Use '\$0 help' to show this message."
    echo "=========================================================="
}

cmd_sync_git() {
    if [ ! -f "$MEMORY_FILE" ]; then
        echo "Error: Memory file $MEMORY_FILE not found." >&2
        exit 1
    fi
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
    local commit
    commit=$(git log -n 1 --format="%h" 2>/dev/null || echo "none")

    # Update memory.md using sed
    sed -i -E "s|- \*\*Active Branch\*\*: .*|- **Active Branch**: $branch|" "$MEMORY_FILE"
    sed -i -E "s|- \*\*Last Commit Reference\*\*: .*|- **Last Commit Reference**: $commit|" "$MEMORY_FILE"
    echo "Synchronized: Branch=$branch, Commit=$commit in $MEMORY_FILE"
}

cmd_lock() {
    local module="${1:-}"
    if [ -z "$module" ]; then
        echo "Error: Please specify a module name to lock." >&2
        exit 1
    fi
    mkdir -p "$LOCKS_DIR"
    # Replace slashes with underscores for nested monorepo paths
    local lock_name="${module//\//_}"
    local lockfile="$LOCKS_DIR/$lock_name.lock"
    if [ -f "$lockfile" ]; then
        echo "Error: Module '$module' is already locked!" >&2
        cat "$lockfile" >&2
        exit 1
    fi

    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    cat << INNER_EOF > "$lockfile"
Branch: $branch
Owner: Agent
Timestamp: $timestamp
INNER_EOF
    echo "Acquired lock for module '$module' at $lockfile"
}

cmd_unlock() {
    local module="${1:-}"
    if [ -z "$module" ]; then
        echo "Error: Please specify a module name to unlock." >&2
        exit 1
    fi
    # Replace slashes with underscores for nested monorepo paths
    local lock_name="${module//\//_}"
    local lockfile="$LOCKS_DIR/$lock_name.lock"
    if [ ! -f "$lockfile" ]; then
        echo "Warning: Module '$module' is not locked." >&2
        exit 0
    fi
    rm -f "$lockfile"
    echo "Released lock for module '$module'"
}

cmd_build() {
    local subprojects_file=".agents/subprojects.sh"
    if [ -f "$subprojects_file" ]; then
        source "$subprojects_file"
        echo "Monorepo detected. Running build compilation..."
        local failed=0
        for sp in "${SUBPROJECTS[@]}"; do
            local path=$(echo "$sp" | cut -d'|' -f1)
            local build_cmd=$(echo "$sp" | cut -d'|' -f3)
            echo "  Building $path ($build_cmd)..."
            if ! (cd "$path" && eval "$build_cmd"); then
                echo "  [FAIL] Build failed in $path" >&2
                failed=1
            fi
        done
        return $failed
    else
        # Fallback to project_rules build command
        local build_line=$(grep "Build validation" .agents/rules/project_rules.md || echo "")
        local build_cmd=$(echo "$build_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
        if [ -n "$build_cmd" ] && [ "$build_cmd" != "echo 'No build command needed'" ]; then
            eval "$build_cmd"
        else
            echo "No build configuration found."
        fi
    fi
}

cmd_lint() {
    local subprojects_file=".agents/subprojects.sh"
    if [ -f "$subprojects_file" ]; then
        source "$subprojects_file"
        local changed_files=""
        changed_files=$(git diff --cached --name-only 2>/dev/null || echo "")
        local failed=0
        local run_all=0
        if [ -z "$changed_files" ]; then
            run_all=1
            echo "No staged changes detected. Running linter on all monorepo modules..."
        else
            echo "Analyzing staged file boundaries for monorepo-aware linting..."
        fi
        
        for sp in "${SUBPROJECTS[@]}"; do
            local path=$(echo "$sp" | cut -d'|' -f1)
            local lint_cmd=$(echo "$sp" | cut -d'|' -f5)
            local should_run=$run_all
            if [ "$should_run" = "0" ]; then
                if echo "$changed_files" | grep -q "^$path/"; then
                    should_run=1
                fi
            fi
            if [ "$should_run" = "1" ]; then
                echo "  Linting $path ($lint_cmd)..."
                if ! (cd "$path" && eval "$lint_cmd"); then
                    echo "  [FAIL] Linter errors found in $path" >&2
                    failed=1
                fi
            else
                echo "  Skipping $path (no staged modifications)."
            fi
        done
        return $failed
    else
        # Fallback to project_rules linter
        local linter_line=$(grep "Linter command" .agents/rules/project_rules.md || echo "")
        local linter_cmd=$(echo "$linter_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
        if [ -n "$linter_cmd" ] && [ "$linter_cmd" != "echo 'No linter found'" ]; then
            eval "$linter_cmd"
        else
            echo "No linter configuration found."
        fi
    fi
}

cmd_test() {
    local subprojects_file=".agents/subprojects.sh"
    if [ -f "$subprojects_file" ]; then
        source "$subprojects_file"
        local changed_files=""
        changed_files=$(git diff --cached --name-only 2>/dev/null || echo "")
        local failed=0
        local run_all=0
        if [ -z "$changed_files" ]; then
            run_all=1
            echo "No staged changes detected. Running tests on all monorepo modules..."
        else
            echo "Analyzing staged file boundaries for monorepo-aware testing..."
        fi
        
        for sp in "${SUBPROJECTS[@]}"; do
            local path=$(echo "$sp" | cut -d'|' -f1)
            local test_cmd=$(echo "$sp" | cut -d'|' -f4)
            local should_run=$run_all
            if [ "$should_run" = "0" ]; then
                if echo "$changed_files" | grep -q "^$path/"; then
                    should_run=1
                fi
            fi
            if [ "$should_run" = "1" ]; then
                echo "  Testing $path ($test_cmd)..."
                if ! (cd "$path" && eval "$test_cmd"); then
                    echo "  [FAIL] Testing suite failed in $path" >&2
                    failed=1
                fi
            else
                echo "  Skipping $path (no staged modifications)."
            fi
        done
        return $failed
    else
        # Fallback to project_rules test runner
        local test_line=$(grep "Test runner command" .agents/rules/project_rules.md || echo "")
        local test_runner=$(echo "$test_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
        if [ -n "$test_runner" ] && [ "$test_runner" != "echo 'No test suite found'" ]; then
            eval "$test_runner"
        else
            echo "No test runner configuration found."
        fi
    fi
}

cmd_archive() {
    if [ ! -f "$MEMORY_FILE" ]; then
        echo "Error: Memory file $MEMORY_FILE not found." >&2
        exit 1
    fi
    mkdir -p "$ARCHIVE_DIR"
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
    # replace slashes in branch name to avoid path issues
    branch_clean=${branch//\//_}
    local archive_file="$ARCHIVE_DIR/sprint_${branch_clean}.md"

    echo "Archiving tasks to $archive_file..."
    
    # Extract checklist from memory.md
    sed -n '/### Sprint Tasks Checklist/,/---/p' "$MEMORY_FILE" | grep -v -- '---' > "$archive_file"

    # Relocate workflow and PR review files to a branch-specific subdirectory
    local branch_archive_dir="$ARCHIVE_DIR/sprint_${branch_clean}"
    mkdir -p "$branch_archive_dir"
    echo "Archiving workflow and PR review files to $branch_archive_dir..."
    find .agents/workflows -maxdepth 1 -name "task_*.md" -exec mv {} "$branch_archive_dir/" \; 2>/dev/null || true
    find .agents/workflows -maxdepth 1 -name "pr_review_*.md" -exec mv {} "$branch_archive_dir/" \; 2>/dev/null || true


    # Reset checklist in memory.md
    local start_line
    start_line=$(grep -n "### Sprint Tasks Checklist" "$MEMORY_FILE" | cut -d: -f1)
    if [ -z "$start_line" ]; then
        echo "Error: Could not locate checklist section in $MEMORY_FILE" >&2
        exit 1
    fi

    local end_line
    end_line=$(tail -n +$start_line "$MEMORY_FILE" | grep -n "^---" | head -n 1 | cut -d: -f1)
    if [ -z "$end_line" ]; then
        end_line=$(wc -l < "$MEMORY_FILE")
    else
        end_line=$((start_line + end_line - 1))
    fi

    local temp_file
    temp_file=$(mktemp)
    head -n "$start_line" "$MEMORY_FILE" > "$temp_file"
    cat << 'INNER_EOF' >> "$temp_file"
- [ ] Implement core logic
- [ ] Write unit tests
- [ ] Verify build and tests pass
INNER_EOF
    tail -n +"$end_line" "$MEMORY_FILE" >> "$temp_file"
    mv "$temp_file" "$MEMORY_FILE"
    echo "Checklist reset successfully."
}

cmd_init() {
    echo "=========================================================="
    echo "  Antigravity Agent Core - Workspace Initialization"
    echo "=========================================================="
    
    local project_name="${2:-}"
    local tech_stack="${3:-}"
    local arch_pattern="${4:-}"
    local db_orm="${5:-}"
    local env_vars="${6:-}"
    local scaffold=""
    local be_choice="1"
    local be_arch_choice="2"
    local fe_choice="1"
    local fe_arch_choice="2"
    local gen_docker=""

    if [ -z "$project_name" ]; then
        read -p "Enter Project Name (default: My Project): " project_name
        if [ -z "$project_name" ]; then project_name="My Project"; fi
    fi
    
    if [ -z "$tech_stack" ]; then
        echo "Select Technology Stack:"
        echo "  [1] Next.js (TypeScript, Tailwind, App Router) [Recommended]"
        echo "  [2] Go Gin (Clean Architecture REST API)"
        echo "  [3] FastAPI (Python REST API with pytest)"
        echo "  [4] Node/TypeScript (Generic Node App)"
        echo "  [5] Go (Generic Main App)"
        echo "  [6] Python (Generic Script)"
        echo "  [7] Monorepo (Turborepo: Next.js Frontend + Go Gin Backend)"
        echo "  [8] Custom Multi-Project / Separate Apps (e.g. apps/backend + apps/frontend)"
        echo "  [9] Laravel (PHP MVC Framework)"
        read -p "Select choice [1-9] (default: 1): " stack_choice
        case "$stack_choice" in
            2) tech_stack="Go Gin" ;;
            3) tech_stack="FastAPI" ;;
            4) tech_stack="Node/TypeScript" ;;
            5) tech_stack="Go" ;;
            6) tech_stack="Python" ;;
            7) tech_stack="Monorepo" ;;
            8) tech_stack="Multi-Project" ;;
            9) tech_stack="Laravel" ;;
            1|"") tech_stack="Next.js" ;;
            *) tech_stack="$stack_choice" ;;
        esac
    fi

    if [ "$tech_stack" = "Multi-Project" ]; then
        echo ""
        echo "--- Configure Backend Application ---"
        echo "  [1] NestJS (TypeScript)"
        echo "  [2] FastAPI (Python)"
        echo "  [3] Go Gin"
        echo "  [4] None"
        read -p "Select Backend Choice [1-4] (default: 1): " be_choice
        if [ -z "$be_choice" ]; then be_choice="1"; fi

        if [ "$be_choice" != "4" ]; then
            echo "Configure Backend Architecture:"
            echo "  [1] Hexagonal Architecture (Ports & Adapters)"
            echo "  [2] Clean Architecture"
            echo "  [3] Standard MVC / Modular"
            read -p "Select Architecture [1-3] (default: 2): " be_arch_choice
            if [ -z "$be_arch_choice" ]; then be_arch_choice="2"; fi
        fi

        echo ""
        echo "--- Configure Frontend Application ---"
        echo "  [1] Next.js (TypeScript)"
        echo "  [2] React SPA (Vite)"
        echo "  [3] Laravel Blade / PHP HTML"
        echo "  [4] None"
        read -p "Select Frontend Choice [1-4] (default: 1): " fe_choice
        if [ -z "$fe_choice" ]; then fe_choice="1"; fi

        if [ "$fe_choice" != "4" ]; then
            echo "Configure Frontend Architecture:"
            echo "  [1] Atomic Design"
            echo "  [2] Standard Components / App Router Layout"
            read -p "Select Architecture [1-2] (default: 2): " fe_arch_choice
            if [ -z "$fe_arch_choice" ]; then fe_arch_choice="2"; fi
        fi
        
        arch_pattern="Decoupled / Distributed Architecture"
        db_orm="None"
        env_vars="PORT"
    fi

    # Auto-suggest architecture based on stack
    local default_arch="MVC"
    if [ "$tech_stack" = "Next.js" ]; then
        default_arch="App Router"
    elif [ "$tech_stack" = "Go Gin" ]; then
        default_arch="Clean Architecture"
    elif [ "$tech_stack" = "FastAPI" ]; then
        default_arch="Modular REST"
    elif [ "$tech_stack" = "Monorepo" ]; then
        default_arch="Decoupled / Distributed"
    elif [ "$tech_stack" = "Laravel" ]; then
        default_arch="MVC"
    fi

    if [ -z "$arch_pattern" ]; then
        read -p "Enter Architectural Pattern (default: $default_arch): " arch_pattern
        if [ -z "$arch_pattern" ]; then arch_pattern="$default_arch"; fi
    fi

    # Auto-suggest env vars based on stack
    local default_env="PORT"
    if [ "$tech_stack" = "Go Gin" ] || [ "$tech_stack" = "FastAPI" ]; then
        default_env="PORT,ENV"
    elif [ "$tech_stack" = "Next.js" ]; then
        default_env="PORT"
    elif [ "$tech_stack" = "Laravel" ]; then
        default_env="APP_KEY,DB_CONNECTION,DB_DATABASE"
    fi

    if [ -z "$db_orm" ]; then
        read -p "Enter Database/ORM (e.g. Prisma, PostgreSQL, None) (default: None): " db_orm
        if [ -z "$db_orm" ]; then db_orm="None"; fi
    fi

    if [ -z "$env_vars" ]; then
        read -p "Enter config variables (comma-separated) (default: $default_env): " env_vars
        if [ -z "$env_vars" ]; then env_vars="$default_env"; fi
    fi

    if [ -z "${7:-}" ]; then
        read -p "Scaffold initial project folders? (y/n) (default: y): " scaffold
        if [ -z "$scaffold" ]; then scaffold="y"; fi
    else
        scaffold="${7:-}"
    fi

    if [ -z "${8:-}" ]; then
        read -p "Generate Dockerfiles and docker-compose.yml? (y/n) (default: y): " gen_docker
        if [ -z "$gen_docker" ]; then gen_docker="y"; fi
    else
        gen_docker="${8:-}"
    fi

    # Initialize Git if not present
    if [ ! -d .git ]; then
        echo "Initializing Git repository..."
        git init
        git branch -m main
    fi

    # Install Git hooks (pre-commit & post-commit)
    mkdir -p .git/hooks
    if [ -f .agents/hooks/pre-commit ]; then
        cp .agents/hooks/pre-commit .git/hooks/pre-commit
        chmod +x .git/hooks/pre-commit
        echo "Git pre-commit hook installed."
    fi
    if [ -f .agents/hooks/post-commit ]; then
        cp .agents/hooks/post-commit .git/hooks/post-commit
        chmod +x .git/hooks/post-commit
        echo "Git post-commit hook installed."
    fi
    if [ -f .agents/hooks/commit-msg ]; then
        cp .agents/hooks/commit-msg .git/hooks/commit-msg
        chmod +x .git/hooks/commit-msg
        echo "Git commit-msg hook installed."
    fi

    # Scaffolding folders if requested
    if [ "$scaffold" = "y" ] || [ "$scaffold" = "yes" ]; then
        echo "Scaffolding directory structure..."
        
        if [ "$tech_stack" = "Next.js" ]; then
            if [[ "$arch_pattern" =~ "Atomic" || "$arch_pattern" =~ "atomic" ]]; then
                mkdir -p src/app src/components/atoms src/components/molecules src/components/organisms src/components/templates src/lib tests
            elif [[ "$arch_pattern" =~ "Clean" || "$arch_pattern" =~ "clean" ]]; then
                mkdir -p src/app src/core/entities src/core/usecases src/infrastructure/db src/infrastructure/api src/lib tests
            else
                mkdir -p src/app src/components src/lib tests
            fi
            # Write package.json
            cat << 'JSON_EOF' > package.json
{
  "name": "nextjs-boilerplate",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest"
  },
  "dependencies": {
    "next": "^14.2.3",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/node": "^20.12.12",
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.3",
    "typescript": "^5.4.5",
    "eslint": "^8.57.0",
    "eslint-config-next": "^14.2.3",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.4"
  }
}
JSON_EOF
            # Write next.config.js
            cat << 'JS_EOF' > next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

module.exports = nextConfig;
JS_EOF
            # Write tailwind.config.js
            cat << 'JS_EOF' > tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
JS_EOF
            # Write postcss.config.js
            cat << 'JS_EOF' > postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
JS_EOF
            # Write tsconfig.json
            cat << 'JSON_EOF' > tsconfig.json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
JSON_EOF
            # Write jest.config.js
            cat << 'JS_EOF' > jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.ts'],
};
JS_EOF
            # Write src/app/globals.css
            cat << 'CSS_EOF' > src/app/globals.css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  color-scheme: dark;
}

body {
  margin: 0;
  padding: 0;
  background-color: #020617;
  color: #f8fafc;
}
CSS_EOF
            # Write src/app/layout.tsx
            cat << 'TSX_EOF' > src/app/layout.tsx
import React from 'react';
import './globals.css';

export const metadata = {
  title: 'Antigravity Next.js Boilerplate',
  description: 'Scaffolded Next.js workspace for AI software agents',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
TSX_EOF
            # Write src/app/page.tsx
            cat << 'TSX_EOF' > src/app/page.tsx
import React from 'react';

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 font-sans">
      <div className="max-w-4xl w-full text-center space-y-8">
        <header className="space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-sm font-semibold tracking-wide animate-pulse">
            🚀 Antigravity Workspace Active
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            Antigravity Next.js Boilerplate
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Your production-ready Next.js application, scaffolded and pre-configured for seamless development with AI coding agents.
          </p>
        </header>

        <main className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-indigo-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">⚡ App Router</h2>
            <p className="text-slate-400 text-sm">
              Scaffolded with React Server Components, layout sharing, and clean directory structure inside <code className="text-indigo-400">src/app</code>.
            </p>
          </div>
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-purple-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">🎨 Styling & UI</h2>
            <p className="text-slate-400 text-sm">
              Pre-integrated with Tailwind CSS, custom fonts, CSS variables, and modern dark-mode aesthetics ready for immediate extension.
            </p>
          </div>
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-pink-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">🛡️ AI Agent Guard</h2>
            <p className="text-slate-400 text-sm">
              Wrapped inside Antigravity's cognitive alignment gates (automated pre-commit validators, secret scanning, and memory sync).
            </p>
          </div>
        </main>

        <footer className="text-slate-500 text-sm border-t border-slate-900 pt-8 mt-12 flex justify-between items-center">
          <div> Muhammad Rafael Ghifari &copy; 2026</div>
          <div className="flex gap-4">
            <a href="https://github.com/rafaelghif/antigravity-agents" target="_blank" rel="noopener noreferrer" className="hover:text-indigo-400 transition-colors">GitHub Repository</a>
            <a href="/api/health" className="hover:text-indigo-400 transition-colors">API Health Check</a>
          </div>
        </footer>
      </div>
    </div>
  );
}
TSX_EOF
            # Write src/app/api/health/route.ts
            mkdir -p src/app/api/health
            cat << 'TS_EOF' > src/app/api/health/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'HEALTHY',
    timestamp: new Date().toISOString(),
    system: 'Antigravity Workspace Core',
  });
}
TS_EOF
            # Write tests/health.test.ts
            cat << 'TS_EOF' > tests/health.test.ts
describe('Next.js Boilerplate Test Suite', () => {
  it('should pass initial unit test check', () => {
    expect(true).toBe(true);
  });
});
TS_EOF
            echo "Scaffolded Next.js application template successfully!"

        elif [ "$tech_stack" = "Go Gin" ]; then
            if [[ "$arch_pattern" =~ "Hexagonal" || "$arch_pattern" =~ "hexagonal" || "$arch_pattern" =~ "Ports" || "$arch_pattern" =~ "ports" ]]; then
                mkdir -p src/cmd/server src/internal/core/domain src/internal/core/ports src/internal/adapters/in/web src/internal/adapters/out/db src/internal/config tests
            elif [[ "$arch_pattern" =~ "Clean" || "$arch_pattern" =~ "clean" ]]; then
                mkdir -p src/cmd/server src/internal/domain/entity src/internal/domain/usecase src/internal/adapter/controller src/internal/adapter/repository src/internal/infrastructure/db src/internal/config tests
            else
                mkdir -p src/cmd/server src/internal/model src/internal/controller src/internal/view src/internal/config tests
            fi
            # Write go.mod
            cat << 'GO_EOF' > go.mod
module project

go 1.20

require (
	github.com/gin-gonic/gin v1.9.1
)
GO_EOF
            # Write src/cmd/server/main.go
            cat << 'GO_EOF' > src/cmd/server/main.go
package main

import (
	"fmt"
	"log"
	"net/http"
	"project/src/internal/config"
	"project/src/internal/controller"

	"github.com/gin-gonic/gin"
)

func main() {
	cfg := config.LoadConfig()

	if cfg.Env == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.Default()
	r.Use(gin.Recovery())

	healthCtrl := controller.NewHealthController()

	api := r.Group("/api")
	{
		api.GET("/health", healthCtrl.Check)
	}

	r.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "Welcome to Antigravity Go Gin Boilerplate!",
			"status":  "Active",
		})
	})

	addr := fmt.Sprintf(":%s", cfg.Port)
	log.Printf("Server starting on port %s...", cfg.Port)
	if err := r.Run(addr); err != nil {
		log.Fatalf("Failed to run server: %v", err)
	}
}
GO_EOF
            # Write src/internal/config/config.go
            cat << 'GO_EOF' > src/internal/config/config.go
package config

import "os"

type Config struct {
	Port string
	Env  string
}

func LoadConfig() *Config {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	env := os.Getenv("ENV")
	if env == "" {
		env = "development"
	}
	return &Config{
		Port: port,
		Env:  env,
	}
}
GO_EOF
            # Write src/internal/controller/health_controller.go
            cat << 'GO_EOF' > src/internal/controller/health_controller.go
package controller

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

type HealthController struct{}

func NewHealthController() *HealthController {
	return &HealthController{}
}

func (h *HealthController) Check(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "HEALTHY",
		"timestamp": time.Now().Format(time.RFC3339),
		"system":    "Antigravity Go Gin Core",
	})
}
GO_EOF
            # Write tests/health_test.go
            cat << 'GO_EOF' > tests/health_test.go
package tests

import (
	"net/http"
	"net/http/httptest"
	"project/src/internal/controller"
	"testing"

	"github.com/gin-gonic/gin"
)

func TestHealthCheck(t *testing.T) {
	gin.SetMode(gin.TestMode)
	r := gin.Default()
	healthCtrl := controller.NewHealthController()
	r.GET("/api/health", healthCtrl.Check)

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/api/health", nil)
	r.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status code 200, got %d", w.Code)
	}
}
GO_EOF
            # Write Makefile
            cat << 'MAKE_EOF' > Makefile
.PHONY: run test build clean

run:
	go run src/cmd/server/main.go

test:
	go test -v ./tests/...

build:
	go build -o bin/server src/cmd/server/main.go

clean:
	rm -rf bin/
MAKE_EOF
            echo "Scaffolded Go Gin application template successfully!"

        elif [ "$tech_stack" = "FastAPI" ]; then
            if [[ "$arch_pattern" =~ "Hexagonal" || "$arch_pattern" =~ "hexagonal" || "$arch_pattern" =~ "Ports" || "$arch_pattern" =~ "ports" ]]; then
                mkdir -p src/app/domain src/app/ports src/app/adapters/in/api src/app/adapters/out/db src/app/core tests
            elif [[ "$arch_pattern" =~ "Clean" || "$arch_pattern" =~ "clean" ]]; then
                mkdir -p src/app/entities src/app/usecases src/app/controllers src/app/infrastructure/db src/app/core tests
            else
                mkdir -p src/app/core src/app/api/endpoints tests
            fi
            # Write requirements.txt
            cat << 'TXT_EOF' > requirements.txt
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.4
pytest>=8.1.1
httpx>=0.27.0
TXT_EOF
            # Write pyproject.toml
            cat << 'TOML_EOF' > pyproject.toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
TOML_EOF
            # Write src/app/main.py
            cat << 'PY_EOF' > src/app/main.py
import uvicorn
from fastapi import FastAPI
from src.app.core.config import settings
from src.app.api.endpoints import health

app = FastAPI(
    title="Antigravity FastAPI Boilerplate",
    description="Production-ready FastAPI setup for AI software agents",
    version="1.0.0",
)

app.include_router(health.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Antigravity FastAPI Boilerplate!",
        "status": "Active",
    }

if __name__ == "__main__":
    uvicorn.run("src.app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
PY_EOF
            # Write src/app/core/config.py
            cat << 'PY_EOF' > src/app/core/config.py
import os

class Settings:
    PORT: int = int(os.getenv("PORT", 8000))
    ENV: str = os.getenv("ENV", "development")

settings = Settings()
PY_EOF
            # Write src/app/api/endpoints/health.py
            cat << 'PY_EOF' > src/app/api/endpoints/health.py
from datetime import datetime
from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["system"])
def check_health():
    return {
        "status": "HEALTHY",
        "timestamp": datetime.utcnow().isoformat(),
        "system": "Antigravity FastAPI Core",
    }
PY_EOF
            # Write tests/test_health.py
            cat << 'PY_EOF' > tests/test_health.py
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "timestamp" in data
    assert data["system"] == "Antigravity FastAPI Core"
PY_EOF
            echo "Scaffolded FastAPI application template successfully!"

        elif [ "$tech_stack" = "Monorepo" ]; then
            # Scaffold Turborepo monorepo structure
            mkdir -p apps/web apps/api packages/shared

            # Write root pnpm-workspace.yaml
            cat << 'YAML_EOF' > pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
YAML_EOF

            # Write root turbo.json
            cat << 'JSON_EOF' > turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "dist/**", "bin/**"]
    },
    "lint": {},
    "test": {},
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
JSON_EOF

            # Write root package.json
            cat << 'JSON_EOF' > package.json
{
  "name": "monorepo-root",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "lint": "turbo run lint",
    "test": "turbo run test"
  },
  "devDependencies": {
    "turbo": "^2.0.0"
  }
}
JSON_EOF

            # ----------------------------------------------------
            # 1. Apps: apps/web (Next.js)
            # ----------------------------------------------------
            mkdir -p apps/web/src/app apps/web/src/components apps/web/src/lib apps/web/tests
            
            # package.json for web app
            cat << 'JSON_EOF' > apps/web/package.json
{
  "name": "web",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest"
  },
  "dependencies": {
    "next": "^14.2.3",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "@monorepo/shared": "workspace:*"
  },
  "devDependencies": {
    "@types/node": "^20.12.12",
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.3",
    "typescript": "^5.4.5",
    "eslint": "^8.57.0",
    "eslint-config-next": "^14.2.3",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.4"
  }
}
JSON_EOF

            # next.config.js for web app
            cat << 'JS_EOF' > apps/web/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};
module.exports = nextConfig;
JS_EOF

            # tailwind.config.js for web app
            cat << 'JS_EOF' > apps/web/tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
JS_EOF

            # postcss.config.js for web app
            cat << 'JS_EOF' > apps/web/postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
JS_EOF

            # tsconfig.json for web app
            cat << 'JSON_EOF' > apps/web/tsconfig.json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
JSON_EOF

            # jest.config.js for web app
            cat << 'JS_EOF' > apps/web/jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.ts'],
};
JS_EOF

            # globals.css for web app
            cat << 'CSS_EOF' > apps/web/src/app/globals.css
@tailwind base;
@tailwind components;
@tailwind utilities;
:root {
  color-scheme: dark;
}
body {
  margin: 0;
  padding: 0;
  background-color: #020617;
  color: #f8fafc;
}
CSS_EOF

            # layout.tsx for web app
            cat << 'TSX_EOF' > apps/web/src/app/layout.tsx
import React from 'react';
import './globals.css';
export const metadata = {
  title: 'Antigravity Monorepo Frontend',
  description: 'Scaffolded Turborepo Frontend Web Application',
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
TSX_EOF

            # page.tsx for web app
            cat << 'TSX_EOF' > apps/web/src/app/page.tsx
import React from 'react';
import { appName, version } from '@monorepo/shared';

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 font-sans">
      <div className="max-w-4xl w-full text-center space-y-8">
        <header className="space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-sm font-semibold tracking-wide animate-pulse">
            🚀 Antigravity Monorepo Active
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            {appName}
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Monorepo Web Client (v{version}) running alongside an isolated Go Gin backend service.
          </p>
        </header>
        <main className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-indigo-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">⚡ Next.js</h2>
            <p className="text-slate-400 text-sm">
              Frontend web client running Next.js App Router inside <code className="text-indigo-400">apps/web</code>.
            </p>
          </div>
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-purple-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">🐹 Go Gin API</h2>
            <p className="text-slate-400 text-sm">
              Isolated REST API backend service with Go Gin inside <code className="text-purple-400">apps/api</code>.
            </p>
          </div>
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-pink-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">📦 Shared Workspace</h2>
            <p className="text-slate-400 text-sm">
              Shared package containing index exports, interfaces, and types inside <code className="text-pink-400">packages/shared</code>.
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}
TSX_EOF

            # health route for web app
            mkdir -p apps/web/src/app/api/health
            cat << 'TS_EOF' > apps/web/src/app/api/health/route.ts
import { NextResponse } from 'next/server';
export async function GET() {
  return NextResponse.json({
    status: 'HEALTHY',
    timestamp: new Date().toISOString(),
    system: 'Antigravity Monorepo Frontend',
  });
}
TS_EOF

            # tests for web app
            cat << 'TS_EOF' > apps/web/tests/health.test.ts
describe('Monorepo Web Client Test Suite', () => {
  it('should pass initial tests', () => {
    expect(true).toBe(true);
  });
});
TS_EOF

            # ----------------------------------------------------
            # 2. Apps: apps/api (Go Gin)
            # ----------------------------------------------------
            mkdir -p apps/api/src/cmd/server apps/api/src/internal/controller apps/api/src/internal/config apps/api/tests

            # go.mod for api app
            cat << 'GO_EOF' > apps/api/go.mod
module api

go 1.20

require (
	github.com/gin-gonic/gin v1.9.1
)
GO_EOF

            # main.go for api app
            cat << 'GO_EOF' > apps/api/src/cmd/server/main.go
package main
import (
	"fmt"
	"log"
	"net/http"
	"api/src/internal/config"
	"api/src/internal/controller"
	"github.com/gin-gonic/gin"
)
func main() {
	cfg := config.LoadConfig()
	if cfg.Env == "production" {
		gin.SetMode(gin.ReleaseMode)
	}
	r := gin.Default()
	r.Use(gin.Recovery())
	healthCtrl := controller.NewHealthController()
	api := r.Group("/api")
	{
		api.GET("/health", healthCtrl.Check)
	}
	r.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "Welcome to Antigravity Go Gin Backend in Monorepo!",
			"status":  "Active",
		})
	})
	addr := fmt.Sprintf(":%s", cfg.Port)
	log.Printf("Backend starting on port %s...", cfg.Port)
	if err := r.Run(addr); err != nil {
		log.Fatalf("Failed to run server: %v", err)
	}
}
GO_EOF

            # config.go for api app
            cat << 'GO_EOF' > apps/api/src/internal/config/config.go
package config
import "os"
type Config struct {
	Port string
	Env  string
}
func LoadConfig() *Config {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	env := os.Getenv("ENV")
	if env == "" {
		env = "development"
	}
	return &Config{
		Port: port,
		Env:  env,
	}
}
GO_EOF

            # health_controller.go for api app
            cat << 'GO_EOF' > apps/api/src/internal/controller/health_controller.go
package controller
import (
	"net/http"
	"time"
	"github.com/gin-gonic/gin"
)
type HealthController struct{}
func NewHealthController() *HealthController {
	return &HealthController{}
}
func (h *HealthController) Check(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "HEALTHY",
		"timestamp": time.Now().Format(time.RFC3339),
		"system":    "Antigravity Monorepo Backend API",
	})
}
GO_EOF

            # test for api app
            cat << 'GO_EOF' > apps/api/tests/health_test.go
package tests
import (
	"net/http"
	"net/http/httptest"
	"api/src/internal/controller"
	"testing"
	"github.com/gin-gonic/gin"
)
func TestHealthCheck(t *testing.T) {
	gin.SetMode(gin.TestMode)
	r := gin.Default()
	healthCtrl := controller.NewHealthController()
	r.GET("/api/health", healthCtrl.Check)
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/api/health", nil)
	r.ServeHTTP(w, req)
	if w.Code != http.StatusOK {
		t.Errorf("Expected status code 200, got %d", w.Code)
	}
}
GO_EOF

            # Makefile for api app
            cat << 'MAKE_EOF' > apps/api/Makefile
.PHONY: run test build clean
run:
	go run src/cmd/server/main.go
test:
	go test -v ./tests/...
build:
	go build -o bin/server src/cmd/server/main.go
clean:
	rm -rf bin/
MAKE_EOF

            # ----------------------------------------------------
            # 3. Packages: packages/shared
            # ----------------------------------------------------
            cat << 'JSON_EOF' > packages/shared/package.json
{
  "name": "@monorepo/shared",
  "version": "1.0.0",
  "private": true,
  "main": "index.js",
  "types": "index.d.ts"
}
JSON_EOF

            cat << 'JS_EOF' > packages/shared/index.js
module.exports = {
  appName: "Antigravity Monorepo",
  version: "1.0.0"
};
JS_EOF

            cat << 'TS_EOF' > packages/shared/index.d.ts
export const appName: string;
export const version: string;
TS_EOF

            echo "Scaffolded Monorepo application template successfully!"

        elif [ "$tech_stack" = "Multi-Project" ]; then
            # Scaffold Custom Multi-Project / Separate Apps layout
            mkdir -p apps/backend apps/frontend
            
            echo "Scaffolding Custom Multi-Project layout..."

            # 1. Scaffold Backend App
            if [ "$be_choice" = "1" ]; then
                # NestJS Boilerplate
                echo "  Scaffolding NestJS backend..."
                mkdir -p apps/backend/src
                
                # Check Architecture
                if [ "$be_arch_choice" = "1" ]; then
                    # Hexagonal Architecture
                    mkdir -p apps/backend/src/core/domain apps/backend/src/core/ports apps/backend/src/adapters/in/web apps/backend/src/adapters/out/persistence
                elif [ "$be_arch_choice" = "2" ]; then
                    # Clean Architecture
                    mkdir -p apps/backend/src/entities apps/backend/src/usecases apps/backend/src/controllers apps/backend/src/infrastructure/db
                else
                    # Standard NestJS Modular
                    mkdir -p apps/backend/src/modules apps/backend/src/common
                fi
                
                cat << 'JSON_EOF' > apps/backend/package.json
{
  "name": "backend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "build": "nest build",
    "start": "nest start",
    "lint": "eslint 'src/**/*.ts'",
    "test": "jest"
  },
  "dependencies": {
    "@nestjs/common": "^10.0.0",
    "@nestjs/core": "^10.0.0",
    "reflect-metadata": "^0.1.13",
    "rxjs": "^7.8.1"
  },
  "devDependencies": {
    "@nestjs/cli": "^10.0.0",
    "@nestjs/testing": "^10.0.0",
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "jest": "^29.0.0"
  }
}
JSON_EOF

                cat << 'TS_EOF' > apps/backend/src/main.ts
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  await app.listen(process.env.PORT || 3000);
}
bootstrap();
TS_EOF

                cat << 'TS_EOF' > apps/backend/src/app.module.ts
import { Module } from '@nestjs/common';

@Module({
  imports: [],
  controllers: [],
  providers: [],
})
export class AppModule {}
TS_EOF

            elif [ "$be_choice" = "2" ]; then
                # FastAPI Boilerplate
                echo "  Scaffolding FastAPI backend..."
                mkdir -p apps/backend/src/app
                
                if [ "$be_arch_choice" = "1" ]; then
                    # Hexagonal Architecture
                    mkdir -p apps/backend/src/app/domain apps/backend/src/app/ports apps/backend/src/app/adapters/in/api apps/backend/src/app/adapters/out/db apps/backend/src/app/core
                elif [ "$be_arch_choice" = "2" ]; then
                    # Clean Architecture
                    mkdir -p apps/backend/src/app/entities apps/backend/src/app/usecases apps/backend/src/app/controllers apps/backend/src/app/infrastructure/db apps/backend/src/app/core
                else
                    # Standard Modular API
                    mkdir -p apps/backend/src/app/core apps/backend/src/app/api/endpoints
                fi
                
                cat << 'TXT_EOF' > apps/backend/requirements.txt
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.4
pytest>=8.1.1
httpx>=0.27.0
TXT_EOF

                cat << 'PY_EOF' > apps/backend/src/app/main.py
from fastapi import FastAPI

app = FastAPI(title="Antigravity Custom Backend")

@app.get("/")
def read_root():
    return {"message": "Hello from Custom FastAPI Backend!"}
PY_EOF

            elif [ "$be_choice" = "3" ]; then
                # Go Gin Boilerplate
                echo "  Scaffolding Go Gin backend..."
                mkdir -p apps/backend/src/cmd/server
                
                if [ "$be_arch_choice" = "1" ]; then
                    # Hexagonal Architecture
                    mkdir -p apps/backend/src/internal/core/domain apps/backend/src/internal/core/ports apps/backend/src/internal/adapters/in/web apps/backend/src/internal/adapters/out/db apps/backend/src/internal/config
                elif [ "$be_arch_choice" = "2" ]; then
                    # Clean Architecture
                    mkdir -p apps/backend/src/internal/domain/entity apps/backend/src/internal/domain/usecase apps/backend/src/internal/adapter/controller apps/backend/src/internal/adapter/repository apps/backend/src/internal/infrastructure/db apps/backend/src/internal/config
                else
                    # Standard Go Gin MVC
                    mkdir -p apps/backend/src/internal/model apps/backend/src/internal/controller apps/backend/src/internal/view apps/backend/src/internal/config
                fi
                
                cat << 'GO_EOF' > apps/backend/go.mod
module backend

go 1.20

require (
	github.com/gin-gonic/gin v1.9.1
)
GO_EOF

                cat << 'GO_EOF' > apps/backend/src/cmd/server/main.go
package main

import (
	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()
	r.GET("/", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"message": "Hello from Custom Go Gin Backend!",
		})
	})
	r.Run()
}
GO_EOF
            fi

            # 2. Scaffold Frontend App
            if [ "$fe_choice" = "1" ]; then
                # Next.js Boilerplate
                echo "  Scaffolding Next.js frontend..."
                mkdir -p apps/frontend/src/app apps/frontend/src/lib
                
                if [ "$fe_arch_choice" = "1" ]; then
                    # Atomic Design
                    mkdir -p apps/frontend/src/components/atoms apps/frontend/src/components/molecules apps/frontend/src/components/organisms apps/frontend/src/components/templates
                else
                    # Standard Next.js App Router
                    mkdir -p apps/frontend/src/components
                fi
                
                cat << 'JSON_EOF' > apps/frontend/package.json
{
  "name": "frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest"
  },
  "dependencies": {
    "next": "^14.2.3",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "jest": "^29.0.0"
  }
}
JSON_EOF

                cat << 'TSX_EOF' > apps/frontend/src/app/layout.tsx
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Antigravity Custom Frontend',
  description: 'Flexible separate frontend application',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
TSX_EOF

                cat << 'TSX_EOF' > apps/frontend/src/app/page.tsx
export default function Home() {
  return (
    <main style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>🚀 Welcome to Antigravity Custom Frontend</h1>
      <p>Running alongside a decoupled backend service in a clean modular layout.</p>
    </main>
  );
}
TSX_EOF

            elif [ "$fe_choice" = "2" ]; then
                # React SPA (Vite) Boilerplate
                echo "  Scaffolding React SPA frontend..."
                mkdir -p apps/frontend/src apps/frontend/public
                
                if [ "$fe_arch_choice" = "1" ]; then
                    # Atomic Design
                    mkdir -p apps/frontend/src/components/atoms apps/frontend/src/components/molecules apps/frontend/src/components/organisms apps/frontend/src/components/templates
                else
                    # Standard React Components
                    mkdir -p apps/frontend/src/components
                fi
                
                cat << 'JSON_EOF' > apps/frontend/package.json
{
  "name": "frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint 'src/**/*.ts'",
    "test": "jest"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "jest": "^29.0.0"
  }
}
JSON_EOF

                cat << 'HTML_EOF' > apps/frontend/index.html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Antigravity React SPA</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
HTML_EOF

                cat << 'TSX_EOF' > apps/frontend/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
TSX_EOF

                cat << 'TSX_EOF' > apps/frontend/src/App.tsx
import React from 'react';

export default function App() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>🚀 Welcome to Antigravity React SPA Frontend</h1>
      <p>Decoupled single-page frontend application.</p>
    </div>
  );
}
TSX_EOF

            elif [ "$fe_choice" = "3" ]; then
                # Laravel Blade / PHP HTML Boilerplate
                echo "  Scaffolding Laravel Blade/HTML frontend..."
                mkdir -p apps/frontend/resources/views apps/frontend/public/css apps/frontend/public/js
                
                cat << 'HTML_EOF' > apps/frontend/resources/views/welcome.blade.php
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Antigravity Blade Frontend</title>
    <style>
        body { font-family: sans-serif; padding: 2rem; background-color: #f8fafc; color: #1e293b; }
    </style>
</head>
<body>
    <h1>🚀 Welcome to Antigravity Blade/HTML Frontend</h1>
    <p>Flexible separate frontend application template.</p>
</body>
</html>
HTML_EOF
            fi

            echo "Scaffolded Custom Multi-Project application template successfully!"

        elif [ "$tech_stack" = "Laravel" ]; then
            # Scaffold Laravel Full-stack PHP application
            echo "Scaffolding Laravel Application..."
            # Create standard Laravel directories
            mkdir -p app/Http/Controllers app/Models app/Providers bootstrap config database/migrations database/seeders database/factories public resources/views resources/css resources/js routes tests/Feature tests/Unit
            
            # Write Controller.php
            cat << 'PHP_EOF' > app/Http/Controllers/Controller.php
<?php

namespace App\Http\Controllers;

use Illuminate\Foundation\Auth\Access\AuthorizesRequests;
use Illuminate\Foundation\Validation\ValidatesRequests;
use Illuminate\Routing\Controller as BaseController;

class Controller extends BaseController
{
    use AuthorizesRequests, ValidatesRequests;
}
PHP_EOF

            # Write User.php Model
            cat << 'PHP_EOF' > app/Models/User.php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable;

    protected $fillable = [
        'name',
        'email',
        'password',
    ];

    protected $hidden = [
        'password',
        'remember_token',
    ];

    protected $casts = [
        'email_verified_at' => 'datetime',
        'password' => 'hashed',
    ];
}
PHP_EOF

            # Write composer.json
            cat << 'JSON_EOF' > composer.json
{
    "name": "laravel/laravel",
    "type": "project",
    "description": "The Laravel Framework.",
    "keywords": ["framework", "laravel"],
    "license": "MIT",
    "require": {
        "php": "^8.1",
        "guzzlehttp/guzzle": "^7.2",
        "laravel/framework": "^10.0",
        "laravel/sanctum": "^3.2",
        "laravel/tinker": "^2.8"
    },
    "require-dev": {
        "fakerphp/faker": "^1.9.1",
        "laravel/pint": "^1.0",
        "laravel/sail": "^1.18",
        "mockery/mockery": "^1.4.4",
        "nunomaduro/collision": "^7.0",
        "phpunit/phpunit": "^10.0",
        "spatie/laravel-ignition": "^2.0"
    },
    "autoload": {
        "psr-4": {
            "App\\": "app/",
            "Database\\Factories\\": "database/factories/",
            "Database\\Seeders\\": "database/seeders/"
        }
    },
    "autoload-dev": {
        "psr-4": {
            "Tests\\": "tests/"
        }
    },
    "scripts": {
        "post-autoload-dump": [
            "Illuminate\\Foundation\\ComposerScripts::postAutoloadDump",
            "@php artisan package:discover --ansi"
        ],
        "post-update-cmd": [
            "@php artisan vendor:publish --tag=laravel-assets --ansi --force"
        ],
        "post-root-package-install": [
            "@php -r \"file_exists('.env') || copy('.env.example', '.env');\""
        ],
        "post-create-project-cmd": [
            "@php artisan key:generate --ansi"
        ]
    },
    "extra": {
        "laravel": {
            "dont-discover": []
        }
    },
    "config": {
        "optimize-autoloader": true,
        "preferred-install": "dist",
        "sort-packages": true,
        "allow-plugins": {
            "pestphp/pest-plugin": true,
            "php-http/discovery": true
        }
    },
    "minimum-stability": "stable",
    "prefer-stable": true
}
JSON_EOF

            # Write package.json
            cat << 'JSON_EOF' > package.json
{
    "private": true,
    "type": "module",
    "scripts": {
        "dev": "vite",
        "build": "vite build"
    },
    "devDependencies": {
        "axios": "^1.1.2",
        "laravel-vite-plugin": "^0.7.5",
        "vite": "^4.0.0"
    }
}
JSON_EOF

            # Write .env.example
            cat << 'ENV_EOF' > .env.example
APP_NAME=Laravel
APP_ENV=local
APP_KEY=
APP_DEBUG=true
APP_URL=http://localhost

LOG_CHANNEL=stack
LOG_DEPRECATIONS_CHANNEL=null
LOG_LEVEL=debug

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=laravel
DB_USERNAME=root
DB_PASSWORD=

BROADCAST_DRIVER=log
CACHE_DRIVER=file
FILESYSTEM_DISK=local
QUEUE_CONNECTION=sync
SESSION_DRIVER=file
SESSION_LIFETIME=120
ENV_EOF

            cp .env.example .env

            # Write Artisan executable
            cat << 'ARTISAN_EOF' > artisan
#!/usr/bin/env php
<?php

define('LARAVEL_START', microtime(true));

if (file_exists($maintenance = __DIR__.'/storage/framework/maintenance.php')) {
    require $maintenance;
}

require __DIR__.'/vendor/autoload.php';

$app = require_once __DIR__.'/bootstrap/app.php';

$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);

$status = $kernel->handle(
    $input = new Symfony\Component\Console\Input\ArgvInput,
    new Symfony\Component\Console\Output\ConsoleOutput
);

$kernel->terminate($input, $status);

exit($status);
ARTISAN_EOF
            chmod +x artisan

            # Write bootstrap/app.php
            cat << 'BOOTSTRAP_EOF' > bootstrap/app.php
<?php

$app = new Illuminate\Foundation\Application(
    $_ENV['APP_BASE_PATH'] ?? dirname(__DIR__)
);

$app->singleton(
    Illuminate\Contracts\Http\Kernel::class,
    App\Http\Kernel::class
);

$app->singleton(
    Illuminate\Contracts\Console\Kernel::class,
    App\Http\Console\Kernel::class
);

$app->singleton(
    Illuminate\Contracts\Debug\ExceptionHandler::class,
    App\Exceptions\Handler::class
);

return $app;
BOOTSTRAP_EOF

            # Write App HTTP Kernel, Exceptions, Console, Web routes, Controllers, Welcome views etc.
            mkdir -p app/Http app/Exceptions app/Console
            
            cat << 'KERNEL_EOF' > app/Http/Kernel.php
<?php

namespace App\Http;

use Illuminate\Foundation\Http\Kernel as HttpKernel;

class Kernel extends HttpKernel
{
    protected $middleware = [
        \Illuminate\Http\Middleware\TrustProxies::class,
        \Illuminate\Http\Middleware\HandleCors::class,
        \Illuminate\Foundation\Http\Middleware\PreventRequestsDuringMaintenance::class,
        \Illuminate\Foundation\Http\Middleware\ValidatePostSize::class,
        \App\Http\Middleware\TrimStrings::class,
        \Illuminate\Foundation\Http\Middleware\ConvertEmptyStringsToNull::class,
    ];

    protected $middlewareGroups = [
        'web' => [
            \App\Http\Middleware\EncryptCookies::class,
            \Illuminate\Cookie\Middleware\AddQueuedCookiesToResponse::class,
            \Illuminate\Session\Middleware\StartSession::class,
            \Illuminate\View\Middleware\ShareErrorsFromSession::class,
            \App\Http\Middleware\VerifyCsrfToken::class,
            \Illuminate\Routing\Middleware\SubstituteBindings::class,
        ],
        'api' => [
            \Laravel\Sanctum\Http\Middleware\EnsureFrontendRequestsAreStateful::class,
            \Illuminate\Routing\Middleware\ThrottleRequests::class.':api',
            \Illuminate\Routing\Middleware\SubstituteBindings::class,
        ],
    ];

    protected $middlewareAliases = [
        'auth' => \App\Http\Middleware\Authenticate::class,
        'guest' => \App\Http\Middleware\RedirectIfAuthenticated::class,
        'verified' => \Illuminate\Auth\Middleware\EnsureEmailIsVerified::class,
    ];
}
KERNEL_EOF

            cat << 'CONSOLE_EOF' > app/Console/Kernel.php
<?php

namespace App\Console;

use Illuminate\Foundation\Console\Kernel as ConsoleKernel;

class Kernel extends ConsoleKernel
{
    protected function commands(): void
    {
        $this->load(__DIR__.'/Commands');
        require base_path('routes/console.php');
    }
}
CONSOLE_EOF

            cat << 'HANDLER_EOF' > app/Exceptions/Handler.php
<?php

namespace App\Exceptions;

use Illuminate\Foundation\Exceptions\Handler as ExceptionHandler;
use Throwable;

class Handler extends ExceptionHandler
{
    protected $dontFlash = [
        'current_password',
        'password',
        'password_confirmation',
    ];

    public function register(): void
    {
        $this->reportable(function (Throwable $e) {
            //
        });
    }
}
HANDLER_EOF

            # Middlewares: app/Http/Middleware/
            mkdir -p app/Http/Middleware
            cat << 'MIDDLEWARE_EOF' > app/Http/Middleware/TrimStrings.php
<?php
namespace App\Http\Middleware;
use Illuminate\Foundation\Http\Middleware\TrimStrings as Middleware;
class TrimStrings extends Middleware {}
MIDDLEWARE_EOF

            cat << 'MIDDLEWARE_EOF' > app/Http/Middleware/EncryptCookies.php
<?php
namespace App\Http\Middleware;
use Illuminate\Cookie\Middleware\EncryptCookies as Middleware;
class EncryptCookies extends Middleware {}
MIDDLEWARE_EOF

            cat << 'MIDDLEWARE_EOF' > app/Http/Middleware/VerifyCsrfToken.php
<?php
namespace App\Http\Middleware;
use Illuminate\Foundation\Http\Middleware\VerifyCsrfToken as Middleware;
class VerifyCsrfToken extends Middleware {}
MIDDLEWARE_EOF

            cat << 'MIDDLEWARE_EOF' > app/Http/Middleware/Authenticate.php
<?php
namespace App\Http\Middleware;
use Illuminate\Auth\Middleware\Authenticate as Middleware;
use Illuminate\Http\Request;
class Authenticate extends Middleware {
    protected function redirectTo(Request $request): ?string {
        return $request->expectsJson() ? null : route('login');
    }
}
MIDDLEWARE_EOF

            cat << 'MIDDLEWARE_EOF' > app/Http/Middleware/RedirectIfAuthenticated.php
<?php
namespace App\Http\Middleware;
use App\Providers\RouteServiceProvider;
use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Symfony\Component\HttpFoundation\Response;
class RedirectIfAuthenticated {
    public function handle(Request $request, Closure $next, string ...$guards): Response {
        $guards = empty($guards) ? [null] : $guards;
        foreach ($guards as $guard) {
            if (Auth::guard($guard)->check()) {
                return redirect(RouteServiceProvider::HOME);
            }
        }
        return $next($request);
    }
}
MIDDLEWARE_EOF

            # Providers: app/Providers/
            mkdir -p app/Providers
            cat << 'PROVIDER_EOF' > app/Providers/RouteServiceProvider.php
<?php

namespace App\Providers;

use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Foundation\Support\Providers\RouteServiceProvider as ServiceProvider;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\Facades\Route;

class RouteServiceProvider extends ServiceProvider
{
    public const HOME = '/home';

    public function boot(): void
    {
        RateLimiter::for('api', function (Request $request) {
            return Limit::perMinute(60)->by($request->user()?->id ?: $request->ip());
        });

        $this->routes(function () {
            Route::middleware('api')
                ->prefix('api')
                ->group(base_path('routes/api.php'));

            Route::middleware('web')
                ->group(base_path('routes/web.php'));
        });
    }
}
PROVIDER_EOF

            # Write standard routes
            cat << 'ROUTES_EOF' > routes/web.php
<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});
ROUTES_EOF

            cat << 'ROUTES_EOF' > routes/api.php
<?php

use Illuminate\Support\Facades\Route;
use Illuminate\Http\Request;

Route::middleware('auth:sanctum')->get('/user', function (Request $request) {
    return $request->user();
});
ROUTES_EOF

            cat << 'ROUTES_EOF' > routes/console.php
<?php

use Illuminate\Support\Facades\Artisan;

Artisan::command('inspire', function () {
    $this->comment(Illuminate\Foundation\Inspiring::quote());
})->purpose('Display an inspiring quote');
ROUTES_EOF

            # Write welcome view
            cat << 'HTML_EOF' > resources/views/welcome.blade.php
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Antigravity Laravel Application</title>
    <style>
        body {
            font-family: 'Outfit', 'Inter', sans-serif;
            background: radial-gradient(circle at top right, #1e1b4b, #0f172a);
            color: #f8fafc;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
        }
        .container {
            text-align: center;
            padding: 3rem;
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 24px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            max-width: 500px;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            background: linear-gradient(to right, #f43f5e, #fb7185);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        p {
            color: #94a3b8;
            line-height: 1.6;
        }
        .badge {
            display: inline-block;
            padding: 0.5rem 1rem;
            background: rgba(244, 63, 94, 0.1);
            color: #f43f5e;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="badge">Laravel 10.x + PHP</div>
        <h1>🚀 Welcome to Antigravity Laravel</h1>
        <p>Your production-ready Laravel full-stack MVC application, scaffolded and pre-configured for seamless development with AI coding agents.</p>
    </div>
</body>
</html>
HTML_EOF

            # Write phpunit.xml
            cat << 'XML_EOF' > phpunit.xml
<?xml version="1.0" encoding="UTF-8"?>
<phpunit xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:noNamespaceSchemaLocation="./vendor/phpunit/phpunit/phpunit.xsd"
         bootstrap="vendor/autoload.php"
         colors="true">
    <testsuites>
        <testsuite name="Unit">
            <directory suffix="Test.php">./tests/Unit</directory>
        </testsuite>
        <testsuite name="Feature">
            <directory suffix="Test.php">./tests/Feature</directory>
        </testsuite>
    </testsuites>
</phpunit>
XML_EOF

            echo "Scaffolded Laravel application template successfully!"

        else
            # Generic/Basic Scaffolding Fallback
            mkdir -p src tests config
            if [[ "$tech_stack" =~ "Node" || "$tech_stack" =~ "TypeScript" || "$tech_stack" =~ "TS" ]]; then
                if [ ! -f package.json ]; then
                    cat << 'JSON_EOF' > package.json
{
  "name": "project",
  "version": "1.0.0",
  "description": "",
  "main": "src/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "jest",
    "lint": "eslint 'src/**/*.ts'"
  },
  "dependencies": {},
  "devDependencies": {}
}
JSON_EOF
                    echo "Created package.json scaffolding"
                fi
            fi
            
            if [[ "$tech_stack" =~ "Go" || "$tech_stack" =~ "Golang" ]]; then
                if [ ! -f go.mod ]; then
                    cat << 'GO_EOF' > go.mod
module project

go 1.20
GO_EOF
                    echo "Created go.mod scaffolding"
                fi
                if [ ! -f src/main.go ]; then
                    cat << 'GO_EOF' > src/main.go
package main

import "fmt"

func main() {
    fmt.Println("Hello, Antigravity!")
}
GO_EOF
                    echo "Created src/main.go template"
                fi
            fi

            if [[ "$tech_stack" =~ "Python" || "$tech_stack" =~ "Py" ]]; then
                if [ ! -f src/main.py ]; then
                    cat << 'PY_EOF' > src/main.py
def main():
    print("Hello, Antigravity!")

if __name__ == "__main__":
    main()
PY_EOF
                    echo "Created src/main.py template"
                fi
            fi
        fi

        if [ "$gen_docker" = "y" ] || [ "$gen_docker" = "yes" ]; then
            echo "Generating Dockerfiles and docker-compose.yml..."
            
            # Helper variables for database
            local db_service=""
            local db_envs=""
            local db_depends=""
            
            local db_lower
            db_lower=$(echo "$db_orm" | tr '[:upper:]' '[:lower:]')
            
            if [[ "$db_lower" =~ "postgres" ]]; then
                db_service=$(cat << 'DB_POSTGRES'
  postgres:
    image: postgres:15-alpine
    container_name: postgres_db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
DB_POSTGRES
)
                db_envs="      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres\n      - DB_HOST=postgres\n      - DB_PORT=5432"
                db_depends="    depends_on:\n      postgres:\n        condition: service_healthy"
            elif [[ "$db_lower" =~ "mysql" || "$db_lower" =~ "mariadb" ]]; then
                db_service=$(cat << 'DB_MYSQL'
  mysql:
    image: mysql:8.0
    container_name: mysql_db
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: db
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD-SHELL", "mysqladmin ping -h localhost"]
      interval: 5s
      timeout: 5s
      retries: 5
DB_MYSQL
)
                db_envs="      - DATABASE_URL=mysql://root:root@mysql:3306/db\n      - DB_HOST=mysql\n      - DB_PORT=3306"
                db_depends="    depends_on:\n      mysql:\n        condition: service_healthy"
            elif [[ "$db_lower" =~ "mongo" ]]; then
                db_service=$(cat << 'DB_MONGO'
  mongodb:
    image: mongo:6.0
    container_name: mongodb_db
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    healthcheck:
      test: ["CMD-SHELL", "echo 'db.runCommand(\"ping\")' | mongosh localhost:27017/test --quiet"]
      interval: 5s
      timeout: 5s
      retries: 5
DB_MONGO
)
                db_envs="      - DATABASE_URL=mongodb://mongodb:27017/db\n      - DB_HOST=mongodb\n      - DB_PORT=27017"
                db_depends="    depends_on:\n      mongodb:\n        condition: service_healthy"
            elif [[ "$db_lower" =~ "redis" ]]; then
                db_service=$(cat << 'DB_REDIS'
  redis:
    image: redis:7-alpine
    container_name: redis_cache
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD-SHELL", "redis-cli ping | grep PONG"]
      interval: 5s
      timeout: 5s
      retries: 5
DB_REDIS
)
                db_envs="      - REDIS_URL=redis://redis:6379"
                db_depends="    depends_on:\n      redis:\n        condition: service_healthy"
            fi

            # 1. Monorepo / Multi-Project Scaffolding
            if [ "$tech_stack" = "Monorepo" ] || [ "$tech_stack" = "Multi-Project" ]; then
                local be_dir=""
                local fe_dir=""
                local be_port="3000"
                local fe_port="3000"
                local be_dockerfile=""
                local fe_dockerfile=""
                
                if [ "$tech_stack" = "Monorepo" ]; then
                    be_dir="apps/api"
                    fe_dir="apps/web"
                    be_port="8080" # Go Gin
                    fe_port="3000" # Next.js
                    
                    be_dockerfile=$(cat << 'MONO_BE'
FROM golang:1.20-alpine AS builder
WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main ./src/cmd/server/main.go

FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
MONO_BE
)
                    fe_dockerfile=$(cat << 'MONO_FE'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN \
  if [ -f pnpm-lock.yaml ]; then corepack enable && pnpm i --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
  else npm install; \
  fi
COPY . .
RUN \
  if [ -f pnpm-lock.yaml ]; then pnpm run build; \
  else npm run build; \
  fi

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/package.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]
MONO_FE
)
                else
                    # Multi-Project
                    be_dir="apps/backend"
                    fe_dir="apps/frontend"
                    
                    # Backend Dockerfile selection
                    if [ "$be_choice" = "1" ]; then
                        be_port="3000"
                        be_dockerfile=$(cat << 'MULTI_NEST'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/package.json ./
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/main"]
MULTI_NEST
)
                    elif [ "$be_choice" = "2" ]; then
                        be_port="8000"
                        be_dockerfile=$(cat << 'MULTI_PY'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
MULTI_PY
)
                    elif [ "$be_choice" = "3" ]; then
                        be_port="8080"
                        be_dockerfile=$(cat << 'MULTI_GO'
FROM golang:1.20-alpine AS builder
WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main ./src/cmd/server/main.go

FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
MULTI_GO
)
                    fi

                    # Frontend Dockerfile selection
                    if [ "$fe_choice" = "1" ]; then
                        fe_port="3000"
                        fe_dockerfile=$(cat << 'MULTI_NEXT'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN \
  if [ -f pnpm-lock.yaml ]; then corepack enable && pnpm i --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
  else npm install; \
  fi
COPY . .
RUN \
  if [ -f pnpm-lock.yaml ]; then pnpm run build; \
  else npm run build; \
  fi

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/package.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]
MULTI_NEXT
)
                    elif [ "$fe_choice" = "2" ]; then
                        fe_port="80"
                        fe_dockerfile=$(cat << 'MULTI_VITE'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
MULTI_VITE
)
                    elif [ "$fe_choice" = "3" ]; then
                        fe_port="80"
                        fe_dockerfile=$(cat << 'MULTI_PHP'
FROM php:8.2-apache
COPY . /var/www/html/
RUN chown -R www-data:www-data /var/www/html
EXPOSE 80
MULTI_PHP
)
                    fi
                fi
                
                # Write Dockerfiles
                if [ -n "$be_dockerfile" ] && [ -d "$be_dir" ]; then
                    echo "$be_dockerfile" > "$be_dir/Dockerfile"
                    echo "  Created $be_dir/Dockerfile"
                fi
                if [ -n "$fe_dockerfile" ] && [ -d "$fe_dir" ]; then
                    echo "$fe_dockerfile" > "$fe_dir/Dockerfile"
                    echo "  Created $fe_dir/Dockerfile"
                fi

                # Build docker-compose services
                local services=""
                if [ -d "$be_dir" ] && [ "$be_choice" != "4" ]; then
                    services="${services}\n  backend:\n    build:\n      context: ./${be_dir}\n    ports:\n      - \"${be_port}:${be_port}\"\n"
                    if [ -n "$db_depends" ]; then
                        services="${services}$(echo -e "$db_depends")\n"
                    fi
                    if [ -n "$db_envs" ]; then
                        services="${services}    environment:\n$(echo -e "$db_envs")\n"
                    fi
                fi
                
                if [ -d "$fe_dir" ] && [ "$fe_choice" != "4" ]; then
                    local host_fe_port="3000"
                    if [ "$be_choice" != "4" ] && [ "$be_port" = "3000" ]; then
                        host_fe_port="3001"
                    fi
                    services="${services}\n  frontend:\n    build:\n      context: ./${fe_dir}\n    ports:\n      - \"${host_fe_port}:${fe_port}\"\n"
                    if [ -d "$be_dir" ] && [ "$be_choice" != "4" ]; then
                        services="${services}    depends_on:\n      backend:\n        condition: service_started\n"
                        services="${services}    environment:\n      - BACKEND_URL=http://backend:${be_port}\n"
                    fi
                fi
                
                if [ -n "$db_service" ]; then
                    services="${services}\n$(echo -e "$db_service")"
                fi
                
                # Write docker-compose.yml
                cat << 'COMPOSE_MULTI' > docker-compose.yml
version: '3.8'

services:
COMPOSE_MULTI
                echo -e "$services" >> docker-compose.yml
                cat << 'COMPOSE_VOLUME' >> docker-compose.yml

volumes:
  pgdata:
  mysql_data:
  mongo_data:
  redis_data:
COMPOSE_VOLUME
                echo "  Created docker-compose.yml at root"

            else
                # 2. Single Project Scaffolding
                local port="3000"
                local dockerfile=""
                
                if [ "$tech_stack" = "Next.js" ]; then
                    port="3000"
                    dockerfile=$(cat << 'SINGLE_NEXT'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/package.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]
SINGLE_NEXT
)
                elif [ "$tech_stack" = "Go Gin" ] || [ "$tech_stack" = "Go" ]; then
                    port="8080"
                    dockerfile=$(cat << 'SINGLE_GO'
FROM golang:1.20-alpine AS builder
WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main ./src/cmd/server/main.go

FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
SINGLE_GO
)
                elif [ "$tech_stack" = "FastAPI" ] || [ "$tech_stack" = "Python" ]; then
                    port="8000"
                    dockerfile=$(cat << 'SINGLE_PY'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
SINGLE_PY
)
                elif [ "$tech_stack" = "Node/TypeScript" ]; then
                    port="3000"
                    dockerfile=$(cat << 'SINGLE_NODE'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/package.json ./
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/index.js"]
SINGLE_NODE
)
                fi
                
                if [ -n "$dockerfile" ]; then
                    echo "$dockerfile" > Dockerfile
                    echo "  Created Dockerfile"
                fi

                # Build services for docker-compose.yml
                local services="  app:\n    build:\n      context: .\n    ports:\n      - \"${port}:${port}\"\n"
                if [ -n "$db_depends" ]; then
                    services="${services}$(echo -e "$db_depends")\n"
                fi
                if [ -n "$db_envs" ]; then
                    services="${services}    environment:\n$(echo -e "$db_envs")\n"
                fi
                if [ -n "$db_service" ]; then
                    services="${services}\n$(echo -e "$db_service")"
                fi
                
                # Write docker-compose.yml
                cat << 'COMPOSE_SINGLE' > docker-compose.yml
version: '3.8'

services:
COMPOSE_SINGLE
                echo -e "$services" >> docker-compose.yml
                cat << 'COMPOSE_VOLUME' >> docker-compose.yml

volumes:
  pgdata:
  mysql_data:
  mongo_data:
  redis_data:
COMPOSE_VOLUME
                echo "  Created docker-compose.yml"
            fi
        fi
    fi


    # Create .env and .env.example if env_vars exist
    if [ -n "$env_vars" ]; then
        echo "Writing configuration environment variables..."
        IFS=',' read -ra ADDR <<< "$env_vars"
        # Reset files
        > .env.example
        > .env
        for i in "${ADDR[@]}"; do
            echo "$i=" >> .env.example
            echo "$i=" >> .env
        done
        echo "Created .env and .env.example templates"
    fi

    # Run auto-recon to generate the blueprints
    echo "Running autonomous reconnaissance to populate blueprint files..."
    if [ -f .agents/scripts/recon.sh ]; then
        .agents/scripts/recon.sh -f
    fi

    echo "=========================================================="
    echo "Workspace initialized successfully for '$project_name'!"
    echo "=========================================================="
}

cmd_recon() {
    if [ -f .agents/scripts/recon.sh ]; then
        .agents/scripts/recon.sh
    else
        echo "Error: recon.sh not found at .agents/scripts/recon.sh" >&2
        exit 1
    fi
}

cmd_validate() {
    if [ -f .agents/scripts/validate.sh ]; then
        .agents/scripts/validate.sh
    else
        echo "Error: validate.sh not found at .agents/scripts/validate.sh" >&2
        exit 1
    fi
}

cmd_doctor() {
    echo "=========================================================="
    echo "  Antigravity Workspace Doctor Diagnostics"
    echo "=========================================================="
    
    local errors=0
    
    # Check Git Repository
    if [ -d .git ]; then
        echo "  [PASS] Git repository initialized."
    else
        echo "  [FAIL] Git repository not initialized!"
        errors=$((errors + 1))
    fi
    
    # Check Git hooks
    if [ -f .git/hooks/pre-commit ] && [ -x .git/hooks/pre-commit ]; then
        echo "  [PASS] pre-commit Git hook is installed and executable."
    else
        echo "  [WARNING] Git pre-commit hook is missing or not executable."
        echo "            To install: cp .agents/hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit"
    fi
    if [ -f .git/hooks/post-commit ] && [ -x .git/hooks/post-commit ]; then
        echo "  [PASS] post-commit Git hook is installed and executable."
    else
        echo "  [WARNING] Git post-commit hook is missing or not executable."
        echo "            To install: cp .agents/hooks/post-commit .git/hooks/post-commit && chmod +x .git/hooks/post-commit"
    fi
    if [ -f .git/hooks/commit-msg ] && [ -x .git/hooks/commit-msg ]; then
        echo "  [PASS] commit-msg Git hook is installed and executable."
    else
        echo "  [WARNING] Git commit-msg hook is missing or not executable."
        echo "            To install: cp .agents/hooks/commit-msg .git/hooks/commit-msg && chmod +x .git/hooks/commit-msg"
    fi
    
    # Check helper script executability
    if [ -x .agents/scripts/helper.sh ]; then
        echo "  [PASS] helper.sh is executable."
    else
        echo "  [WARNING] helper.sh is not executable."
        chmod +x .agents/scripts/helper.sh
    fi
    
    # Check recon script
    if [ -f .agents/scripts/recon.sh ]; then
        if [ -x .agents/scripts/recon.sh ]; then
            echo "  [PASS] recon.sh is executable."
        else
            echo "  [WARNING] recon.sh is not executable. Auto-correcting..."
            chmod +x .agents/scripts/recon.sh
        fi
    else
        echo "  [FAIL] recon.sh is missing!"
        errors=$((errors + 1))
    fi

    # Check validate script
    if [ -f .agents/scripts/validate.sh ]; then
        if [ -x .agents/scripts/validate.sh ]; then
            echo "  [PASS] validate.sh is executable."
        else
            echo "  [WARNING] validate.sh is not executable. Auto-correcting..."
            chmod +x .agents/scripts/validate.sh
        fi
    else
        echo "  [FAIL] validate.sh is missing!"
        errors=$((errors + 1))
    fi

    # Run validate.sh checks
    if [ -f .agents/scripts/validate.sh ]; then
        echo "----------------------------------------------------------"
        if ! .agents/scripts/validate.sh; then
            errors=$((errors + 1))
        fi
    fi
    
    echo "=========================================================="
    if [ $errors -eq 0 ]; then
        echo "Doctor diagnostics: ALL SYSTEMS HEALTHY"
        exit 0
    else
        echo "Doctor diagnostics: FOUND $errors ERROR(S) / WARNING(S)"
        exit 1
    fi
}

cmd_commit() {
    local no_test_flag="false"
    local stage_files=()
    local type=""
    local scope=""
    local desc=""

    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --no-test|--no-verify)
                no_test_flag="true"
                shift
                ;;
            *)
                if [ "$1" = "commit" ]; then
                    shift
                elif [ -z "$type" ]; then
                    type="$1"
                    shift
                elif [ -z "$scope" ]; then
                    scope="$1"
                    shift
                elif [ -z "$desc" ]; then
                    desc="$1"
                    shift
                else
                    stage_files+=("$1")
                    shift
                fi
                ;;
        esac
    done

    # Interactive inputs if parameters are missing
    if [ -z "$type" ]; then
        echo "Choose commit type:"
        echo "  [1] feat:     A new feature"
        echo "  [2] fix:      A bug fix"
        echo "  [3] refactor: A code change that neither fixes a bug nor adds a feature"
        echo "  [4] chore:    Changes to the build process or auxiliary tools and libraries"
        echo "  [5] docs:     Documentation only changes"
        echo "  [6] test:     Adding missing tests or correcting existing tests"
        echo "  [7] perf:     A code change that improves performance"
        read -p "Select number or type string (default: feat): " type_choice
        case "$type_choice" in
            1) type="feat" ;;
            2) type="fix" ;;
            3) type="refactor" ;;
            4) type="chore" ;;
            5) type="docs" ;;
            6) type="test" ;;
            7) type="perf" ;;
            "") type="feat" ;;
            *) type="$type_choice" ;;
        esac
    fi

    if [ -z "$scope" ]; then
        read -p "Enter commit scope (e.g. core, auth, db, shared) (default: core): " scope
        if [ -z "$scope" ]; then scope="core"; fi
    fi

    if [ -z "$desc" ]; then
        read -p "Enter brief description of change: " desc
        if [ -z "$desc" ]; then
            echo "Error: Description cannot be empty." >&2
            exit 1
        fi
    fi

    # Workspace Validation
    echo "Running workspace validation checks..."
    if ! .agents/scripts/validate.sh; then
        echo "Error: Workspace validation failed. Aborting commit." >&2
        exit 1
    fi

    # Linter Execution
    if [ "$no_test_flag" = "false" ]; then
        local linter_cmd=""
        if [ -f .agents/rules/project_rules.md ]; then
            local linter_line
            linter_line=$(grep "Linter command" .agents/rules/project_rules.md || echo "")
            linter_cmd=$(echo "$linter_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
        fi

        if [ -n "$linter_cmd" ] && [ "$linter_cmd" != "echo 'No linter found'" ]; then
            echo "Running linter command: $linter_cmd..."
            if ! eval "$linter_cmd"; then
                echo "Error: Linter check failed. Aborting commit." >&2
                exit 1
            fi
            echo "  [PASS] Linter check passed successfully."
        else
            echo "No linter configured in project_rules.md. Skipping linting."
        fi
    else
        echo "Linter check bypassed via --no-test / --no-verify."
    fi

    # Test Execution
    if [ "$no_test_flag" = "false" ]; then
        local test_runner=""
        if [ -f .agents/rules/project_rules.md ]; then
            local test_line
            test_line=$(grep "Test runner command" .agents/rules/project_rules.md || echo "")
            test_runner=$(echo "$test_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
        fi

        if [ -n "$test_runner" ] && [ "$test_runner" != "echo 'No test suite found'" ]; then
            echo "Running test suite: $test_runner..."
            if ! eval "$test_runner"; then
                echo "Error: Test runner suite failed. Aborting commit." >&2
                exit 1
            fi
            echo "  [PASS] All tests passed successfully."
        else
            echo "No test runner configured in project_rules.md. Skipping tests."
        fi
    else
        echo "Test execution bypassed via --no-test / --no-verify."
    fi

    # File Staging
    if [ ${#stage_files[@]} -gt 0 ]; then
        echo "Staging specified files: ${stage_files[*]}..."
        git add "${stage_files[@]}"
    else
        echo "Staging all modified and untracked files..."
        # Check if there are changes to stage
        if [ -n "$(git status --porcelain | grep -v '^\?\? .agents/locks/')" ]; then
            git add -A -- ':!.agents/locks/*'
        fi
    fi

    # Auto-rotate profiles if configured
    local profiles_file=""
    if [ -f ".agents/git_profiles" ]; then
        profiles_file=".agents/git_profiles"
    elif [ -f "$HOME/.git_profiles" ]; then
        profiles_file="$HOME/.git_profiles"
    fi

    if [ -n "$profiles_file" ] && [ -f "$profiles_file" ]; then
        # Get list of profile keys
        local profile_keys
        profile_keys=$(grep -E "^[a-zA-Z0-9_\-]+\.name=" "$profiles_file" | cut -d'.' -f1 | sort -u || echo "")
        
        # Convert to array or list
        local keys_arr=($profile_keys)
        local num_profiles=${#keys_arr[@]}
        
        if [ $num_profiles -gt 0 ]; then
            # Get last commit's author email
            local last_email
            last_email=$(git log -n 1 --format="%ae" 2>/dev/null || echo "")
            
            local selected_idx=0
            # Search if last_email matches any profile's email
            for i in "${!keys_arr[@]}"; do
                local p="${keys_arr[$i]}"
                local p_e=$(grep "^${p}\.email=" "$profiles_file" | cut -d'=' -f2-)
                if [ "$p_e" = "$last_email" ]; then
                    # Select the next profile (round-robin)
                    selected_idx=$(( (i + 1) % num_profiles ))
                    break
                fi
            done
            
            local selected_profile="${keys_arr[$selected_idx]}"
            local p_name=$(grep "^${selected_profile}\.name=" "$profiles_file" | cut -d'=' -f2-)
            local p_email=$(grep "^${selected_profile}\.email=" "$profiles_file" | cut -d'=' -f2-)
            local p_ssh=$(grep "^${selected_profile}\.ssh_key=" "$profiles_file" | cut -d'=' -f2- || echo "")
            
            # Strict Validation of profile fields
            if [ -z "$p_name" ] || [ -z "$p_email" ]; then
                echo "Error: Profile '$selected_profile' is misconfigured in $profiles_file (name and email are required)." >&2
                exit 1
            fi

            echo "Auto-selecting Git profile: '$selected_profile' (\"$p_name\" <$p_email>) for round-robin commit rotation."
            # Set locally
            git config --local user.name "$p_name"
            git config --local user.email "$p_email"
            if [ -n "$p_ssh" ]; then
                local resolved_ssh="$p_ssh"
                if [[ "$resolved_ssh" == \~/* ]]; then
                    resolved_ssh="${resolved_ssh/\~/$HOME}"
                fi
                if [ -f "$resolved_ssh" ]; then
                    echo "Auto-selecting SSH key: '$p_ssh' for profile '$selected_profile'."
                    git config --local core.sshCommand "ssh -i \"$p_ssh\" -o IdentitiesOnly=yes"
                else
                    echo "Warning: SSH key file at '$p_ssh' specified for profile '$selected_profile' does not exist. Bypassing SSH setup." >&2
                    git config --local --unset core.sshCommand 2>/dev/null || true
                fi
            else
                git config --local --unset core.sshCommand 2>/dev/null || true
            fi
        else
            echo "Error: Git profiles file found at $profiles_file but no valid profiles were parsed." >&2
            exit 1
        fi
    else
        # Strict fallback behavior if no profiles file is found
        local active_name=$(git config user.name 2>/dev/null || echo "")
        local active_email=$(git config user.email 2>/dev/null || echo "")
        
        if [ -z "$active_name" ] || [ -z "$active_email" ]; then
            # Fall back to a default local-only profile for convenience
            echo "Warning: No Git profiles config found (.agents/git_profiles) and no default Git identity (user.name/user.email) is configured." >&2
            echo "  [FALLBACK] Configuring temporary local-only identity: \"Local Developer\" <local-dev@localhost>" >&2
            git config --local user.name "Local Developer"
            git config --local user.email "local-dev@localhost"
            git config --local --unset core.sshCommand 2>/dev/null || true
        else
            # Warn if using generic mock emails to prevent bad commits
            if [[ "$active_email" =~ ^[a-zA-Z0-9_\.-]+@(company\.com|gmail\.com|example\.com)$ ]] && [[ "$active_name" =~ ^(Developer|Test|Alice|Bob).* ]]; then
                echo "Warning: Active Git configuration appears to be using a template or placeholder:" >&2
                echo "  Name:  $active_name" >&2
                echo "  Email: $active_email" >&2
                echo "  Please update your credentials or set up '.agents/git_profiles' for enterprise-grade compliance." >&2
            fi

            echo "[INFO] Auto-rotation bypassed (no profiles config). Using active Git identity: \"$active_name\" <$active_email>"
        fi
    fi

    # Conventional Commit Execution
    local commit_msg="$type($scope): $desc"
    echo "Executing conventional commit: '$commit_msg'..."
    if git commit -m "$commit_msg"; then
        echo "Commit successful."
    else
        echo "Error: Git commit failed." >&2
        exit 1
    fi
}

cmd_migrate() {
    echo "=========================================================="
    echo "  Antigravity Agent Core - Workspace Migration (V1.7.4)"
    echo "=========================================================="

    local backup_suffix=".backup"

    # 1. Back up user-controlled files if they exist
    if [ -f "$MEMORY_FILE" ]; then
        echo "Warning: Existing memory file found. Backing up to ${MEMORY_FILE}${backup_suffix}"
        cp "$MEMORY_FILE" "${MEMORY_FILE}${backup_suffix}"
    fi

    if [ -f ".agents/rules/project_rules.md" ]; then
        echo "Warning: Existing project rules blueprint found. Backing up to .agents/rules/project_rules.md${backup_suffix}"
        cp ".agents/rules/project_rules.md" ".agents/rules/project_rules.md${backup_suffix}"
    fi

    if [ -f ".agents/schema.md" ]; then
        echo "Warning: Existing schema index found. Backing up to .agents/schema.md${backup_suffix}"
        cp ".agents/schema.md" ".agents/schema.md${backup_suffix}"
    fi

    # 2. Ensure directories exist
    echo "Re-creating directory structure..."
    mkdir -p .agents/skills/codebase-recon
    mkdir -p .agents/skills/git-ops
    mkdir -p .agents/skills/test-driven-patch
    mkdir -p .agents/skills/infra-provisioner
    mkdir -p .agents/skills/security-ci-audit
    mkdir -p .agents/skills/code-review
    mkdir -p .agents/skills/impact-analysis
    mkdir -p .agents/workflows
    mkdir -p .agents/archive
    mkdir -p .agents/locks
    mkdir -p .agents/schemas
    mkdir -p .agents/scripts
    mkdir -p .agents/hooks
    mkdir -p .agents/rules

    # Check for legacy rules folder and migrate
    if [ -d ".agent/rules" ]; then
        echo "Legacy rules folder .agent/rules found. Migrating to .agents/rules/..."
        if [ "$(ls -A .agent/rules 2>/dev/null)" ]; then
            cp -r .agent/rules/* .agents/rules/
        fi
        rm -rf .agent/rules
        if [ -d ".agent" ] && [ ! "$(ls -A .agent 2>/dev/null)" ]; then
            rm -rf .agent
        fi
        echo "Migration of legacy rules complete."
        if [ -f "$MEMORY_FILE" ]; then
            if ! grep -q "Legacy rules migrated" "$MEMORY_FILE"; then
                sed -i '/## 3. Relayed Context/a - **Migration Log**: Legacy rules migrated from .agent/rules to .agents/rules.' "$MEMORY_FILE"
            fi
        fi
    fi

    # 3. Update Git Hooks
    echo "Updating local Git hooks..."
    if [ -f .agents/hooks/pre-commit ]; then
        if [ -f .git/hooks/pre-commit ] && ! grep -q "Antigravity Agent Git Hook" .git/hooks/pre-commit; then
            echo "  - Backing up existing custom pre-commit hook"
            mv .git/hooks/pre-commit .git/hooks/pre-commit.backup
        fi
        cp .agents/hooks/pre-commit .git/hooks/pre-commit
        chmod +x .git/hooks/pre-commit
        echo "  - Installed pre-commit hook"
    fi
    if [ -f .agents/hooks/post-commit ]; then
        if [ -f .git/hooks/post-commit ] && ! grep -q "Antigravity Agent Git Hook" .git/hooks/post-commit; then
            echo "  - Backing up existing custom post-commit hook"
            mv .git/hooks/post-commit .git/hooks/post-commit.backup
        fi
        cp .agents/hooks/post-commit .git/hooks/post-commit
        chmod +x .git/hooks/post-commit
        echo "  - Installed post-commit hook"
    fi
    if [ -f .agents/hooks/commit-msg ]; then
        if [ -f .git/hooks/commit-msg ] && ! grep -q "Antigravity Agent Git Hook" .git/hooks/commit-msg; then
            echo "  - Backing up existing custom commit-msg hook"
            mv .git/hooks/commit-msg .git/hooks/commit-msg.backup
        fi
        cp .agents/hooks/commit-msg .git/hooks/commit-msg
        chmod +x .git/hooks/commit-msg
        echo "  - Installed commit-msg hook"
    fi

    # 4. Update memory.md schema version
    if [ -f "$MEMORY_FILE" ]; then
        echo "Updating memory ledger schema version to 5.0.0..."
        if grep -Fq "Memory Schema Version" "$MEMORY_FILE"; then
            local temp_mem
            temp_mem=$(mktemp)
            sed -E "s|Memory Schema Version\*\*: [0-9]+\.[0-9]+\.[0-9]+|Memory Schema Version**: 5.0.0|" "$MEMORY_FILE" > "$temp_mem"
            mv "$temp_mem" "$MEMORY_FILE"
        else
            # Prepend schema version header if not found
            local temp_mem
            temp_mem=$(mktemp)
            echo -e "# Agent Core Memory\n\n> **Memory Schema Version**: 5.0.0  \n> **Target System**: Antigravity Agent Core\n> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/rules/project_rules.md](file://./rules/project_rules.md) for execution details. Keep this file under 100 lines at all times.\n" > "$temp_mem"
            tail -n +2 "$MEMORY_FILE" >> "$temp_mem"
            mv "$temp_mem" "$MEMORY_FILE"
        fi
    fi

    # 5. Fix .gitignore configuration
    if [ -f ".gitignore" ]; then
        echo "Validating .gitignore compliance..."
        local temp_git
        temp_git=$(mktemp)
        # remove any lines that ignore .agents or AGENTS.md globally
        grep -v -E "^\.agents/?$" .gitignore | grep -v "^AGENTS.md$" > "$temp_git" || true
        # ensure Locks directory is ignored
        if ! grep -E -q "^\.agents/locks/?" "$temp_git"; then
            echo -e "\n# Ignore agent transient locks\n.agents/locks/" >> "$temp_git"
        fi
        # ensure API configurations and active state files are ignored
        local has_secret_header=0
        for ignore_pattern in ".agents/api_keys" ".agents/active_api_keys" ".agents/active_api_keys.ps1" ".agents/active_api_profile_name"; do
            if ! grep -q "^$ignore_pattern" "$temp_git"; then
                if [ "$has_secret_header" -eq 0 ]; then
                    echo -e "\n# Ignore local agent API key configuration and active state files" >> "$temp_git"
                    has_secret_header=1
                fi
                echo "$ignore_pattern" >> "$temp_git"
            fi
        done
        mv "$temp_git" ".gitignore"
        echo "  - .gitignore updated."
    else
        echo "Creating default compliant .gitignore..."
        cat << 'GIT_EOF' > .gitignore
# Ignore agent transient locks
.agents/locks/

# Ignore local agent API key configuration and active state files
.agents/api_keys
.agents/active_api_keys
.agents/active_api_keys.ps1
.agents/active_api_profile_name
GIT_EOF
    fi

    # 6. Re-run codebase stack reconstruction (forces regeneration of blueprints)
    echo "Running autonomous stack reconstruction..."
    if [ -f .agents/scripts/recon.sh ]; then
        .agents/scripts/recon.sh -f
    fi

    echo "=========================================================="
    echo "Migration Complete! Workspace successfully upgraded."
    echo "=========================================================="
}

cmd_sync_api() {
    echo "=========================================================="
    echo "Starting API Contract Synchronization..."
    echo "=========================================================="
    
    local subprojects_file=".agents/subprojects.sh"
    local be_path=""
    local fe_path=""
    local be_stack=""
    
    # 1. Detect backend and frontend directories
    if [ -f "$subprojects_file" ]; then
        source "$subprojects_file"
        for sp in "${SUBPROJECTS[@]}"; do
            local path=$(echo "$sp" | cut -d'|' -f1)
            local stack=$(echo "$sp" | cut -d'|' -f2)
            
            # Simple heuristics to identify backend vs frontend
            if [[ "$path" =~ "api" || "$path" =~ "backend" || "$stack" =~ "Go" || "$stack" =~ "Python" ]]; then
                be_path="$path"
                be_stack="$stack"
            elif [[ "$path" =~ "web" || "$path" =~ "frontend" || "$stack" =~ "Next.js" ]]; then
                fe_path="$path"
            fi
        done
    else
        # Fallback search if no subprojects config file
        if [ -d "apps/backend" ]; then be_path="apps/backend"; fi
        if [ -d "apps/frontend" ]; then fe_path="apps/frontend"; fi
        if [ -d "apps/api" ]; then be_path="apps/api"; fi
        if [ -d "apps/web" ]; then fe_path="apps/web"; fi
    fi
    
    # If still not found, search directories
    if [ -z "$be_path" ]; then
        if [ -f "go.mod" ] || [ -f "main.go" ]; then
            be_path="."
            be_stack="Go"
        elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
            be_path="."
            be_stack="Python"
        fi
    fi
    if [ -z "$fe_path" ]; then
        if [ -d "src/app" ] || [ -f "package.json" ]; then
            fe_path="."
        fi
    fi

    if [ -z "$be_path" ]; then
        echo "  [INFO] Backend application path could not be auto-detected. Operating in root fallback mode."
        be_path="."
        be_stack="Unknown"
    fi
    
    echo "  Detected Backend: $be_path ($be_stack)"
    if [ -n "$fe_path" ]; then
        echo "  Detected Frontend: $fe_path"
    fi

    local openapi_file="openapi.json"
    
    # 2. Extract OpenAPI schema from backend
    echo "  Extracting OpenAPI contract schema..."
    
    if [[ "$be_stack" =~ "Python" || -f "$be_path/requirements.txt" || -f "$be_path/pyproject.toml" ]]; then
        # Python / FastAPI extraction
        if [ "$be_path" = "." ]; then
            python3 -c "import json; from src.app.main import app; print(json.dumps(app.openapi()))" > "$openapi_file" 2>/dev/null || \
            python3 -c "import json; from app.main import app; print(json.dumps(app.openapi()))" > "$openapi_file" 2>/dev/null || \
            echo "Failed to extract FastAPI schema. Ensure FastAPI app is importable."
        else
            (cd "$be_path" && python3 -c "import json; from src.app.main import app; print(json.dumps(app.openapi()))" > "../../../$openapi_file" 2>/dev/null || \
            (cd "$be_path" && python3 -c "import json; from app.main import app; print(json.dumps(app.openapi()))" > "../../../$openapi_file" 2>/dev/null)) || \
            echo "Failed to extract FastAPI schema. Ensure FastAPI app is importable."
        fi
    elif [[ "$be_stack" =~ "Go" || -f "$be_path/go.mod" ]]; then
        # Go Swagger check
        if command -v swag &> /dev/null; then
            echo "  Running swag init in $be_path..."
            (cd "$be_path" && swag init -g src/cmd/server/main.go -o . --ot json && cp swagger.json ../../$openapi_file) 2>/dev/null || \
            (cd "$be_path" && swag init -g cmd/server/main.go -o . --ot json && cp swagger.json ../../$openapi_file) 2>/dev/null || \
            echo "Swag command failed. Creating mockup/fallback schema."
        fi
    fi

    # Fallback/Mockup schema if extraction failed or file is empty/missing
    if [ ! -f "$openapi_file" ] || [ ! -s "$openapi_file" ]; then
        echo "  Warning: Schema extraction returned empty. Writing a compliant mock/fallback openapi.json..."
        cat << 'MOCK_OPENAPI' > "$openapi_file"
{
  "openapi": "3.0.0",
  "info": {
    "title": "Antigravity Mock API",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "http://localhost:3000"
    }
  ],
  "paths": {
    "/api/users": {
      "get": {
        "operationId": "get_users",
        "responses": {
          "200": {
            "description": "Success",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/User"
                  }
                }
              }
            }
          }
        }
      },
      "post": {
        "operationId": "create_user",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/User"
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Created",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/User"
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "User": {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
          "id": {
            "type": "integer"
          },
          "name": {
            "type": "string"
          },
          "email": {
            "type": "string"
          }
        }
      }
    }
  }
}
MOCK_OPENAPI
    fi

    # 3. Generate TypeScript API client
    if [ -n "$fe_path" ] && [ -d "$fe_path" ]; then
        local target_client="$fe_path/src/lib/api-client.ts"
        if [ "$fe_path" = "." ] && [ -d "src/app" ]; then
            target_client="src/lib/api-client.ts"
        fi
        
        echo "  Generating TypeScript client wrapper to $target_client..."
        node .agents/scripts/generate-client.js "$openapi_file" "$target_client"
    else
        echo "  Frontend directory not detected. Generated openapi.json is saved in root."
    fi

    echo "=========================================================="
    echo "API Sync Complete!"
    echo "=========================================================="
}

cmd_log_usage() {
    if [ $# -lt 2 ]; then
        echo "Usage: $0 log-usage <token_count> [profile_name]"
        exit 1
    fi
    local count="$2"
    local profile="${3:-}"
    
    # Auto-detect profile from active_api_profile_name if not specified
    if [ -z "$profile" ]; then
        if [ -f ".agents/active_api_profile_name" ]; then
            profile=$(cat ".agents/active_api_profile_name" | xargs)
        else
            profile="default"
        fi
    fi

    local file=".agents/token_budget.json"
    if [ ! -f "$file" ]; then
        echo "{\"max_token_budget\": 500000, \"current_token_usage\": 0, \"alert_threshold_percent\": 90, \"profiles\": {}}" > "$file"
    fi

    if command -v jq >/dev/null 2>&1; then
        local current_global=$(jq -r '.current_token_usage // 0' "$file")
        local new_global=$((current_global + count))
        
        local current_profile=$(jq -r --arg prof "$profile" '.profiles[$prof].current_token_usage // 0' "$file")
        local new_profile_usage=$((current_profile + count))
        
        local temp=$(mktemp)
        jq --argjson g_use "$new_global" \
           --arg prof "$profile" \
           --argjson p_use "$new_profile_usage" \
           '.current_token_usage = $g_use | .profiles[$prof].current_token_usage = $p_use | .profiles[$prof].max_token_budget //= 500000' \
           "$file" > "$temp"
        mv "$temp" "$file"
        echo "Logged $count tokens for profile '$profile'. Total profile usage: $new_profile_usage. Global usage: $new_global."
    elif command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1; then
        local py_cmd="python3"
        if ! command -v python3 >/dev/null 2>&1; then py_cmd="python"; fi
        $py_cmd -c "
import json
file_path = '$file'
count = $count
profile = '$profile'
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
except Exception:
    data = {'max_token_budget': 500000, 'current_token_usage': 0, 'alert_threshold_percent': 90, 'profiles': {}}

data['current_token_usage'] = data.get('current_token_usage', 0) + count
if 'profiles' not in data:
    data['profiles'] = {}
if profile not in data['profiles']:
    data['profiles'][profile] = {'max_token_budget': 500000, 'current_token_usage': 0}
data['profiles'][profile]['current_token_usage'] = data['profiles'][profile].get('current_token_usage', 0) + count

with open(file_path, 'w') as f:
    json.dump(data, f, indent=2)
"
        echo "Logged $count tokens for profile '$profile' (fallback). Updated $file."
    else
        # minimal fallback using sed (global only)
        local current=$(grep -o '"current_token_usage":\s*[0-9]*' "$file" | grep -o '[0-9]*' || echo "0")
        local new_usage=$((current + count))
        sed -i "s/\"current_token_usage\":\s*[0-9]*/\"current_token_usage\": $new_usage/" "$file"
        echo "Logged $count tokens (global fallback). Updated $file."
    fi
}

cmd_create_adr() {
    if [ $# -lt 2 ]; then
        echo "Usage: $0 create-adr <title> [proposed|accepted|superseded]"
        exit 1
    fi
    local title="$2"
    local status="${3:-proposed}"
    
    # Normalize status to lowercase
    status=$(echo "$status" | tr '[:upper:]' '[:lower:]')
    
    if [ "$status" != "proposed" ] && [ "$status" != "accepted" ] && [ "$status" != "superseded" ]; then
        echo "Error: Status must be one of: proposed, accepted, superseded" >&2
        exit 1
    fi
    
    # Capitalize status for presentation (Proposed, Accepted, Superseded)
    local status_cap
    if [ "$status" = "proposed" ]; then
        status_cap="Proposed"
    elif [ "$status" = "accepted" ]; then
        status_cap="Accepted"
    else
        status_cap="Superseded"
    fi

    local adrs_dir=".agents/adrs"
    mkdir -p "$adrs_dir"
    
    # Determine the next ADR number
    local count=1
    for f in "$adrs_dir"/[0-9][0-9][0-9]-*.md; do
        if [ -e "$f" ]; then
            count=$((count + 1))
        fi
    done
    
    local num
    num=$(printf "%03d" "$count")
    
    # Convert title to kebab-case for filename (lowercase, replace non-alphanumeric with hyphens)
    local slug
    slug=$(echo "$title" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g' | sed -E 's/^-+|-+$//g')
    
    local filename="$adrs_dir/${num}-${slug}.md"
    
    local adr_date
    adr_date=$(date +%Y-%m-%d)
    
    # Write ADR template
    cat << INNER_EOF > "$filename"
# ADR-${num}: ${title}

- **Date**: ${adr_date}
- **Status**: ${status_cap}

## Context
[Describe the problem context and alternatives]

## Decision
[Describe the decision made]

## Consequences
[Describe the result and impact of this decision]
INNER_EOF

    # Register in .agents/adr.md
    local index_file=".agents/adr.md"
    if [ -f "$index_file" ]; then
        # Check if "## 1. Architectural Decisions Index" exists, if not create it
        if ! grep -q "## 1. Architectural Decisions Index" "$index_file"; then
            echo -e "\n## 1. Architectural Decisions Index" >> "$index_file"
        fi
        # Append the link
        echo "- [ADR-${num}: ${title}](file://./adrs/${num}-${slug}.md) - Status: ${status_cap}" >> "$index_file"
    fi
    
    echo "Created ADR-${num} at $filename and registered in $index_file"
}

cmd_release() {
    if [ $# -lt 2 ]; then
        echo "Usage: $0 release <major|minor|patch>"
        exit 1
    fi
    local bump_type="$2"
    local changelog_file="CHANGELOG.md"
    
    if [ ! -f "$changelog_file" ]; then
        echo "Error: CHANGELOG.md not found!"
        exit 1
    fi
    
    # Extract latest version from CHANGELOG.md (e.g. ## [1.4.0] - 2026-06-13)
    local current_version
    current_version=$(grep -m 1 -E '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' "$changelog_file" | grep -o -E '[0-9]+\.[0-9]+\.[0-9]+')
    
    if [ -z "$current_version" ]; then
        echo "Error: Could not parse current version from CHANGELOG.md."
        exit 1
    fi
    
    local major=$(echo "$current_version" | cut -d. -f1)
    local minor=$(echo "$current_version" | cut -d. -f2)
    local patch=$(echo "$current_version" | cut -d. -f3)
    
    case "$bump_type" in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            echo "Error: Invalid bump type '$bump_type'. Must be major, minor, or patch."
            exit 1
            ;;
    esac
    
    local next_version="$major.$minor.$patch"
    local current_date=$(date +%Y-%m-%d)
    
    echo "Bumping version: $current_version -> $next_version ($bump_type)"
    
    # 1. Insert new version section at the top of the version list in CHANGELOG.md
    local temp_changelog=$(mktemp)
    awk -v next_ver="$next_version" -v date="$current_date" '
        BEGIN { done = 0 }
        /^## \[[0-9]+\.[0-9]+\.[0-9]+\]/ && done == 0 {
            print "## [" next_ver "] - " date;
            print "### Added";
            print "- ";
            print "";
            done = 1
        }
        { print }
    ' "$changelog_file" > "$temp_changelog"
    
    # 2. Update version comparison links at the bottom
    local repo_url="https://github.com/rafaelghif/antigravity-agents"
    local temp_links=$(mktemp)
    awk -v next_ver="$next_version" -v curr_ver="$current_version" -v url="$repo_url" '
        BEGIN { link_inserted = 0 }
        /^\[[0-9]+\.[0-9]+\.[0-9]+\]:/ && link_inserted == 0 {
            print "[" next_ver "]: " url "/compare/v" curr_ver "...v" next_ver;
            link_inserted = 1
        }
        { print }
    ' "$temp_changelog" > "$temp_links"
    
    mv "$temp_links" "$changelog_file"
    rm -f "$temp_changelog"
    
    echo "Successfully bumped version to $next_version and updated CHANGELOG.md."
}

audit_skill() {
    local skill_dir="$1"
    local skill_name=$(basename "$skill_dir")
    local skill_md="$skill_dir/SKILL.md"
    
    # Check 1: SKILL.md exists
    if [ ! -f "$skill_md" ]; then
        echo "FAIL: $skill_name is missing SKILL.md"
        return 1
    fi
    
    # Check 2: Parse YAML frontmatter
    local line1=$(head -n 1 "$skill_md" | tr -d '\r')
    if [ "$line1" != "---" ]; then
        echo "FAIL: $skill_name SKILL.md does not start with YAML frontmatter delimiter (---)"
        return 1
    fi
    
    local closing_line=$(grep -n "^---" "$skill_md" | sed -n '2p' | cut -d':' -f1)
    if [ -z "$closing_line" ]; then
        echo "FAIL: $skill_name SKILL.md has unclosed YAML frontmatter"
        return 1
    fi
    
    local frontmatter=$(sed -n "2,$((closing_line - 1))p" "$skill_md")
    
    local parsed_name=$(echo "$frontmatter" | grep "^name:" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e "s/^'//" -e "s/'$//" -e 's/^"//' -e 's/"$//')
    local parsed_desc=$(echo "$frontmatter" | grep "^description:" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e "s/^'//" -e "s/'$//" -e 's/^"//' -e 's/"$//')
    
    if [ -z "$parsed_name" ]; then
        echo "FAIL: $skill_name frontmatter missing 'name'"
        return 1
    fi
    if [ -z "$parsed_desc" ]; then
        echo "FAIL: $skill_name frontmatter missing 'description'"
        return 1
    fi
    
    # Check 3: Check for placeholders in SKILL.md
    if grep -i -q -E "TODO|FIXME|\[placeholder\]" "$skill_md"; then
        echo "FAIL: $skill_name SKILL.md contains placeholder text (TODO/FIXME/placeholder)"
        return 1
    fi
    
    # Check 4: Verify referenced scripts
    local in_scripts=0
    local script_lines=""
    while IFS= read -r line; do
        if [[ "$line" =~ ^scripts:[[:space:]]*$ ]]; then
            in_scripts=1
            continue
        elif [[ "$line" =~ ^[a-zA-Z_]+: ]]; then
            in_scripts=0
        fi
        
        if [ "$in_scripts" -eq 1 ]; then
            script_lines="$script_lines"$'\n'"$line"
        fi
    done <<INNER_EOF
$frontmatter
INNER_EOF

    while IFS= read -r s_line; do
        s_line=$(echo "$s_line" | sed -e 's/^[[:space:]]*-//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
        if [ -n "$s_line" ]; then
            local script_path="$skill_dir/$s_line"
            if [ ! -f "$script_path" ]; then
                echo "FAIL: $skill_name referenced script $s_line does not exist"
                return 1
            fi
            if [ ! -x "$script_path" ]; then
                echo "FAIL: $skill_name referenced script $s_line is not executable (missing chmod +x)"
                return 1
            fi
        fi
    done <<INNER_EOF
$script_lines
INNER_EOF

    if [ -d "$skill_dir/scripts" ]; then
        for f in "$skill_dir/scripts"/*; do
            if [ -f "$f" ]; then
                if [ ! -x "$f" ]; then
                    echo "FAIL: $skill_name script $(basename "$f") is not executable"
                    return 1
                fi
                if grep -i -q -E "TODO|FIXME|\[placeholder\]" "$f"; then
                    echo "FAIL: $skill_name script $(basename "$f") contains placeholder text (TODO/FIXME/placeholder)"
                    return 1
                fi
            fi
        done
    fi
    
    echo "PASS: $parsed_name ($parsed_desc)"
    return 0
}

cmd_create_skill() {
    if [ $# -lt 2 ]; then
        echo "Usage: $0 create-skill <name> [description]"
        exit 1
    fi
    local name="$2"
    local desc="${3:-}"
    
    if [[ ! "$name" =~ ^[a-z0-9-]+$ ]]; then
        echo "Error: Skill name must be lowercase kebab-case (e.g., custom-skill-name)." >&2
        exit 1
    fi
    
    local skill_dir=".agents/skills/$name"
    if [ -d "$skill_dir" ]; then
        echo "Error: Skill '$name' already exists at $skill_dir." >&2
        exit 1
    fi
    
    mkdir -p "$skill_dir/scripts"
    
    cat << INNER_EOF > "$skill_dir/SKILL.md"
---
name: $name
description: ${desc:-Specialized skill for $name automation.}
scripts:
  - scripts/main.py
---

# ${name} Skill

## 1. Input Specification
- Specify required inputs (e.g., target file paths, options).

## 2. Operational Procedures
1. Run the associated script.
2. Verify results.

## 3. Decision Matrix
- If the script returns success (exit code 0), the action is accepted.
- If the script returns error, it fails.

## 4. Error Mitigation Tree
- Retry execution.
- If it fails, report details back to the user.

## 5. Output Verification Gate
- [ ] Executable script passes all internal checks.
INNER_EOF

    cat << INNER_EOF > "$skill_dir/scripts/main.py"
#!/usr/bin/env python3
import argparse
import sys
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_skill(args):
    """
    Main logic of the skill script.
    """
    logging.info(f"Running skill with arguments: {args}")
    # Implement operational logic here
    
    result = {
        "status": "success",
        "message": "Skill $name executed successfully",
        "data": {}
    }
    return result

def main():
    parser = argparse.ArgumentParser(description="Default Python script for agent skill $name.")
    parser.add_argument('--target', type=str, help="Target path or resource")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")
    
    args = parser.parse_args()
    
    try:
        output = run_skill(args)
        print(json.dumps(output, indent=2))
        sys.exit(0)
    except Exception as e:
        logging.error(f"Execution failed: {str(e)}")
        error_output = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(error_output, indent=2))
        sys.exit(1)

if __name__ == '__main__':
    main()
INNER_EOF

    chmod +x "$skill_dir/scripts/main.py"
    echo "Skill '$name' created successfully at $skill_dir"
}

cmd_list_skills() {
    local skills_dir=".agents/skills"
    if [ ! -d "$skills_dir" ]; then
        echo "Error: Skills directory $skills_dir not found." >&2
        exit 1
    fi
    
    echo "=========================================================="
    echo "          Antigravity Agent Skills Audit & Registry"
    echo "=========================================================="
    
    local audit_failed=0
    printf "%-25s | %-12s | %s\n" "Skill Name" "Status" "Description"
    echo "----------------------------------------------------------"
    
    for dir in "$skills_dir"/*; do
        if [ -d "$dir" ]; then
            local skill_name=$(basename "$dir")
            local audit_res
            local exit_code=0
            if ! audit_res=$(audit_skill "$dir" 2>&1); then
                exit_code=1
            fi
            
            local status="[PASS]"
            local detail=""
            if [ $exit_code -eq 0 ]; then
                detail=$(echo "$audit_res" | sed -E 's/^PASS: [^ ]+ \((.*)\)/\1/')
            else
                status="[FAIL]"
                detail=$(echo "$audit_res" | sed -E 's/^FAIL: //')
                audit_failed=$((audit_failed + 1))
            fi
            
            printf "%-25s | %-12s | %s\n" "$skill_name" "$status" "$detail"
        fi
    done
    
    echo "=========================================================="
    if [ $audit_failed -eq 0 ]; then
        echo "All skills are compliant and ready for use."
        return 0
    else
        echo "Audit failed! Found $audit_failed non-compliant skill(s)." >&2
        return 1
    fi
}

audit_rule() {
    local rule_file="$1"
    local rule_name=$(basename "$rule_file" .md)
    
    # Check 1: Must be .md extension
    if [[ ! "$rule_file" =~ \.md$ ]]; then
        echo "FAIL: $rule_name is not a markdown file"
        return 1
    fi
    
    # Check 2: Parse YAML frontmatter
    local line1=$(head -n 1 "$rule_file" | tr -d '\r')
    if [ "$line1" != "---" ]; then
        echo "FAIL: $rule_name does not start with YAML frontmatter delimiter (---)"
        return 1
    fi
    
    local closing_line=$(grep -n "^---" "$rule_file" | sed -n '2p' | cut -d':' -f1)
    if [ -z "$closing_line" ]; then
        echo "FAIL: $rule_name has unclosed YAML frontmatter"
        return 1
    fi
    
    local frontmatter=$(sed -n "2,$((closing_line - 1))p" "$rule_file")
    
    local parsed_name=$(echo "$frontmatter" | grep "^name:" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e "s/^'//" -e "s/'$//" -e 's/^"//' -e 's/"$//')
    local parsed_activation=$(echo "$frontmatter" | grep "^activation:" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e "s/^'//" -e "s/'$//" -e 's/^"//' -e 's/"$//')
    
    if [ -z "$parsed_name" ]; then
        echo "FAIL: $rule_name frontmatter missing 'name'"
        return 1
    fi
    
    if [ -z "$parsed_activation" ]; then
        echo "FAIL: $rule_name frontmatter missing 'activation'"
        return 1
    fi
    
    # Check 3: Validate activation parameters
    case "$parsed_activation" in
        "Manual"|"Always On")
            ;;
        "Glob")
            local parsed_pattern=$(echo "$frontmatter" | grep "^pattern:" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e "s/^'//" -e "s/'$//" -e 's/^"//' -e 's/"$//')
            if [ -z "$parsed_pattern" ]; then
                echo "FAIL: $rule_name activation is Glob but missing 'pattern'"
                return 1
            fi
            ;;
        "Model Decision")
            local parsed_desc=$(echo "$frontmatter" | grep "^description:" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e "s/^'//" -e "s/'$//" -e 's/^"//' -e 's/"$//')
            if [ -z "$parsed_desc" ]; then
                echo "FAIL: $rule_name activation is Model Decision but missing 'description'"
                return 1
            fi
            ;;
        *)
            echo "FAIL: $rule_name has invalid activation mode '$parsed_activation'"
            return 1
            ;;
    esac
    
    # Check 4: Check for placeholders in rule body
    if grep -i -q -E "TODO|FIXME|\[placeholder\]" "$rule_file"; then
        echo "FAIL: $rule_name contains placeholder text (TODO/FIXME/placeholder)"
        return 1
    fi
    
    # Return activation details for tabulated output
    local details="$parsed_activation"
    if [ "$parsed_activation" = "Glob" ]; then
        local parsed_pattern=$(echo "$frontmatter" | grep "^pattern:" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e "s/^'//" -e "s/'$//" -e 's/^"//' -e 's/"$//')
        details="Glob ($parsed_pattern)"
    elif [ "$parsed_activation" = "Model Decision" ]; then
        local parsed_desc=$(echo "$frontmatter" | grep "^description:" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e "s/^'//" -e "s/'$//" -e 's/^"//' -e 's/"$//')
        details="Model Decision ($parsed_desc)"
    fi
    
    echo "PASS: $parsed_name ($details)"
    return 0
}

cmd_create_rule() {
    if [ $# -lt 3 ]; then
        echo "Usage: $0 create-rule <name> <activation> [description_or_pattern]"
        exit 1
    fi
    local name="$2"
    local activation="$3"
    local param="${4:-}"
    
    if [[ ! "$name" =~ ^[a-z0-9-]+$ ]]; then
        echo "Error: Rule name must be lowercase kebab-case (e.g., custom-rule-name)." >&2
        exit 1
    fi
    
    local activation_mode=""
    case "$activation" in
        manual) activation_mode="Manual" ;;
        always-on) activation_mode="Always On" ;;
        model-decision) activation_mode="Model Decision" ;;
        glob) activation_mode="Glob" ;;
        *)
            echo "Error: Invalid activation mode '$activation'. Must be: manual, always-on, model-decision, or glob." >&2
            exit 1
            ;;
    esac
    
    local pattern=""
    local description=""
    if [ "$activation_mode" = "Glob" ]; then
        if [ -z "$param" ]; then
            echo "Error: Glob activation requires a glob pattern parameter (e.g., 'src/**/*.ts')." >&2
            exit 1
        fi
        pattern="$param"
    elif [ "$activation_mode" = "Model Decision" ]; then
        if [ -z "$param" ]; then
            echo "Error: Model Decision activation requires a natural language description parameter." >&2
            exit 1
        fi
        description="$param"
    fi
    
    local rule_file=".agents/rules/$name.md"
    if [ -f "$rule_file" ]; then
        echo "Error: Rule '$name' already exists at $rule_file." >&2
        exit 1
    fi
    
    mkdir -p ".agents/rules"
    
    cat << INNER_EOF > "$rule_file"
---
name: $name
activation: $activation_mode
$( [ -n "$pattern" ] && echo "pattern: \"$pattern\"" )
$( [ -n "$description" ] && echo "description: \"$description\"" )
---

# ${name} Workspace Rule

## Guidelines
- Define the coding standard or instructions for this rule here.
- Example: Prefer arrow functions over traditional function syntax.
INNER_EOF

    echo "Rule '$name' created successfully at $rule_file"
}

cmd_list_rules() {
    local rules_dir=".agents/rules"
    if [ ! -d "$rules_dir" ]; then
        echo "Error: Rules directory $rules_dir not found." >&2
        exit 1
    fi
    
    echo "=========================================================="
    echo "          Antigravity Agent Rules Audit & Registry"
    echo "=========================================================="
    
    local audit_failed=0
    printf "%-25s | %-12s | %s\n" "Rule Name" "Status" "Activation Mode"
    echo "----------------------------------------------------------"
    
    local file_found=0
    for file in "$rules_dir"/*; do
        if [ -f "$file" ]; then
            file_found=1
            local rule_name=$(basename "$file")
            local audit_res
            local exit_code=0
            if ! audit_res=$(audit_rule "$file" 2>&1); then
                exit_code=1
            fi
            
            local status="[PASS]"
            local detail=""
            if [ $exit_code -eq 0 ]; then
                detail=$(echo "$audit_res" | sed -E 's/^PASS: [^ ]+ \((.*)\)/\1/')
            else
                status="[FAIL]"
                detail=$(echo "$audit_res" | sed -E 's/^FAIL: //')
                audit_failed=$((audit_failed + 1))
            fi
            
            printf "%-25s | %-12s | %s\n" "$rule_name" "$status" "$detail"
        fi
    done
    
    if [ $file_found -eq 0 ]; then
        echo "No rules registered in $rules_dir."
    fi
    
    echo "=========================================================="
    if [ $audit_failed -eq 0 ]; then
        echo "All rules are compliant and active."
        return 0
    else
        echo "Audit failed! Found $audit_failed non-compliant rule(s)." >&2
        return 1
    fi
}

cmd_git_profile() {
    if [ ! -d .git ]; then
        echo "Error: Not a Git repository." >&2
        exit 1
    fi

    local name=""
    local email=""
    if [ "${2:-}" = "git-profile" ]; then
        name="${3:-}"
        email="${4:-}"
    else
        name="${2:-}"
        email="${3:-}"
    fi

    # Find profiles config file
    local profiles_file=""
    if [ -f ".agents/git_profiles" ]; then
        profiles_file=".agents/git_profiles"
    elif [ -f "$HOME/.git_profiles" ]; then
        profiles_file="$HOME/.git_profiles"
    fi

    # Check if we should rotate manually
    local is_key_rotate=0
    if [ -n "$profiles_file" ] && grep -q "^rotate\.name=" "$profiles_file"; then
        is_key_rotate=1
    fi

    if ( [ "$name" = "rotate" ] || [ "$name" = "--rotate" ] ) && [ $is_key_rotate -eq 0 ]; then
        if [ -n "$profiles_file" ] && [ -f "$profiles_file" ]; then
            local profile_keys
            profile_keys=$(grep -E "^[a-zA-Z0-9_\-]+\.name=" "$profiles_file" | cut -d'.' -f1 | sort -u || echo "")
            local keys_arr=($profile_keys)
            local num_profiles=${#keys_arr[@]}
            if [ $num_profiles -gt 0 ]; then
                local last_email
                last_email=$(git log -n 1 --format="%ae" 2>/dev/null || echo "")
                local selected_idx=0
                for i in "${!keys_arr[@]}"; do
                    local p="${keys_arr[$i]}"
                    local p_e=$(grep "^${p}\.email=" "$profiles_file" | cut -d'=' -f2-)
                    if [ "$p_e" = "$last_email" ]; then
                        selected_idx=$(( (i + 1) % num_profiles ))
                        break
                    fi
                done
                name="${keys_arr[$selected_idx]}"
                echo "Rotating local Git profile to: '$name'..."
            else
                echo "Error: No profiles defined in $profiles_file." >&2
                exit 1
            fi
        else
            echo "Error: No Git profiles configuration found (.agents/git_profiles) to rotate." >&2
            exit 1
        fi
    fi

    # Check if a single argument matches a profile key in the config file
    if [ -n "$name" ] && [ -z "$email" ] && [ -n "$profiles_file" ] && grep -q "^${name}\.name=" "$profiles_file"; then
        local p_n=$(grep "^${name}\.name=" "$profiles_file" | cut -d'=' -f2-)
        local p_e=$(grep "^${name}\.email=" "$profiles_file" | cut -d'=' -f2-)
        local p_s=$(grep "^${name}\.ssh_key=" "$profiles_file" | cut -d'=' -f2- || echo "")
        echo "Setting local repository Git configuration to profile '$name'..."
        git config --local user.name "$p_n"
        git config --local user.email "$p_e"
        if [ -n "$p_s" ]; then
            local resolved_ssh="$p_s"
            if [[ "$resolved_ssh" == \~/* ]]; then
                resolved_ssh="${resolved_ssh/\~/$HOME}"
            fi
            if [ -f "$resolved_ssh" ]; then
                git config --local core.sshCommand "ssh -i \"$p_s\" -o IdentitiesOnly=yes"
            else
                echo "  [WARNING] SSH key file at '$p_s' was not found on your system. Bypassing SSH command setup." >&2
                git config --local --unset core.sshCommand 2>/dev/null || true
            fi
        else
            git config --local --unset core.sshCommand 2>/dev/null || true
        fi
        echo "  [SUCCESS] Local Git profile updated."
        name=""
        email=""
    fi

    if [ -n "$name" ] && [ -n "$email" ]; then
        echo "Setting local repository Git configuration..."
        git config --local user.name "$name"
        git config --local user.email "$email"
        git config --local --unset core.sshCommand 2>/dev/null || true
        echo "  [SUCCESS] Local Git profile updated."
    elif [ -n "$name" ] || [ -n "$email" ]; then
        if [ -n "$profiles_file" ]; then
            echo "Error: Profile '$name' not found in $profiles_file." >&2
        else
            echo "Error: Both name and email are required to set a profile." >&2
        fi
        echo "Usage:" >&2
        echo "  $0 git-profile [name] [email]   (Set profile directly)" >&2
        echo "  $0 git-profile [profile-key]   (Set from profiles config file)" >&2
        exit 1
    fi

    echo "=========================================================="
    echo "          Current Git User Configuration"
    echo "=========================================================="
    local local_name=$(git config --local user.name 2>/dev/null || echo "<not set>")
    local local_email=$(git config --local user.email 2>/dev/null || echo "<not set>")
    local local_ssh=$(git config --local core.sshCommand 2>/dev/null || echo "<not set>")
    local global_name=$(git config --global user.name 2>/dev/null || echo "<not set>")
    local global_email=$(git config --global user.email 2>/dev/null || echo "<not set>")
    local global_ssh=$(git config --global core.sshCommand 2>/dev/null || echo "<not set>")

    echo "Local Profile (This Repository):"
    echo "  user.name:        $local_name"
    echo "  user.email:       $local_email"
    echo "  core.sshCommand:  $local_ssh"
    echo ""
    echo "Global Profile (Default):"
    echo "  user.name:        $global_name"
    echo "  user.email:       $global_email"
    echo "  core.sshCommand:  $global_ssh"
    echo ""

    if [ -f "$profiles_file" ]; then
        echo "Available Profiles (from $profiles_file):"
        local profiles
        profiles=$(grep -E "^[a-zA-Z0-9_\-]+\.name=" "$profiles_file" | cut -d'.' -f1 | sort -u)
        for p in $profiles; do
            local p_n=$(grep "^${p}\.name=" "$profiles_file" | cut -d'=' -f2-)
            local p_e=$(grep "^${p}\.email=" "$profiles_file" | cut -d'=' -f2-)
            local p_s=$(grep "^${p}\.ssh_key=" "$profiles_file" | cut -d'=' -f2- || echo "")
            if [ -n "$p_s" ]; then
                echo "  - $p: \"$p_n\" <$p_e> (ssh_key: $p_s)"
            else
                echo "  - $p: \"$p_n\" <$p_e>"
            fi
        done
    fi
    echo "=========================================================="
}

cmd_api_profile() {
    local target_profile="${2:-}"
    
    # Find api_keys config file
    local api_keys_file=""
    if [ -f ".agents/api_keys" ]; then
        api_keys_file=".agents/api_keys"
    elif [ -f "$HOME/.antigravity_api_keys" ]; then
        api_keys_file="$HOME/.antigravity_api_keys"
    fi

    # Check if we should rotate
    if [ "$target_profile" = "rotate" ] || [ "$target_profile" = "--rotate" ]; then
        if [ -n "$api_keys_file" ] && [ -f "$api_keys_file" ]; then
            # Parse all profile prefixes
            local api_profiles
            api_profiles=$(grep -E "^[a-zA-Z0-9_\-]+\.[A-Z0-9_]+=" "$api_keys_file" | cut -d'.' -f1 | sort -u || echo "")
            local profiles_arr=($api_profiles)
            local num_profiles=${#profiles_arr[@]}
            
            if [ $num_profiles -gt 0 ]; then
                # Find current profile name from .agents/active_api_profile_name
                local current_profile="none"
                if [ -f ".agents/active_api_profile_name" ]; then
                    current_profile=$(cat ".agents/active_api_profile_name" | xargs)
                fi
                
                local selected_idx=0
                for i in "${!profiles_arr[@]}"; do
                    if [ "${profiles_arr[$i]}" = "$current_profile" ]; then
                        selected_idx=$(( (i + 1) % num_profiles ))
                        break
                    fi
                done
                target_profile="${profiles_arr[$selected_idx]}"
                echo "Rotating active API profile to: '$target_profile'..."
            else
                echo "Error: No API profiles found in $api_keys_file." >&2
                exit 1
            fi
        else
            echo "Error: No API keys configuration found (.agents/api_keys or ~/.antigravity_api_keys) to rotate." >&2
            exit 1
        fi
    fi

    if [ -n "$target_profile" ]; then
        if [ -n "$api_keys_file" ] && [ -f "$api_keys_file" ]; then
            if grep -E -q "^${target_profile}\.[A-Z0-9_]+=" "$api_keys_file"; then
                echo "Setting active API profile to '$target_profile'..."
                
                # Write to .agents/active_api_keys (bash format)
                echo "# Active API keys for profile: $target_profile" > .agents/active_api_keys
                # Write to .agents/active_api_keys.ps1 (powershell format)
                echo "# Active API keys for profile: $target_profile" > .agents/active_api_keys.ps1
                
                # Extract all keys for target_profile
                local key_lines
                key_lines=$(grep -E "^${target_profile}\.[A-Z0-9_]+=" "$api_keys_file" || echo "")
                
                while IFS= read -r line; do
                    if [ -n "$line" ]; then
                        # format is: prefix.VAR_NAME=value
                        local var_name_val="${line#*.}"  # VAR_NAME=value
                        local var_name="${var_name_val%%=*}"
                        local var_val="${var_name_val#*=}"
                        
                        echo "export $var_name=\"$var_val\"" >> .agents/active_api_keys
                        echo "\$env:$var_name = \"$var_val\"" >> .agents/active_api_keys.ps1
                    fi
                done <<< "$key_lines"
                
                # Store active profile name
                echo "$target_profile" > .agents/active_api_profile_name
                echo "  [SUCCESS] Active API keys updated in .agents/active_api_keys and .agents/active_api_keys.ps1"
            else
                echo "Error: Profile '$target_profile' not found in $api_keys_file." >&2
                exit 1
            fi
        else
            echo "Error: API keys file not found (.agents/api_keys or ~/.antigravity_api_keys)." >&2
            exit 1
        fi
    fi

    # Display active profile details
    echo "=========================================================="
    echo "          Current API Profile Configuration"
    echo "=========================================================="
    local active_profile="<none>"
    if [ -f ".agents/active_api_profile_name" ]; then
        active_profile=$(cat ".agents/active_api_profile_name" | xargs)
    fi
    echo "Active Profile: $active_profile"
    echo ""
    if [ -f ".agents/active_api_keys" ]; then
        echo "Active Keys (masked for security):"
        while IFS= read -r line; do
            if [[ "$line" =~ ^export\ ([A-Z0-9_]+)=\"(.+)\"$ ]]; then
                local var_name="${BASH_REMATCH[1]}"
                local var_val="${BASH_REMATCH[2]}"
                local val_len=${#var_val}
                local masked_val="..."
                if [ $val_len -gt 8 ]; then
                    masked_val="${var_val:0:4}****${var_val: -4}"
                fi
                echo "  $var_name: $masked_val"
            fi
        done < .agents/active_api_keys
    else
        echo "Active Keys: <none>"
    fi
    echo ""
    if [ -f "$api_keys_file" ]; then
        echo "Available API Profiles (from $api_keys_file):"
        local profiles
        profiles=$(grep -E "^[a-zA-Z0-9_\-]+\.[A-Z0-9_]+=" "$api_keys_file" | cut -d'.' -f1 | sort -u || echo "")
        for p in $profiles; do
            local keys_in_p
            keys_in_p=$(grep -E "^${p}\.[A-Z0-9_]+=" "$api_keys_file" | cut -d'.' -f2- | cut -d'=' -f1 | tr '\n' ' ' || echo "")
            echo "  - $p ($keys_in_p)"
        done
    fi
    echo "=========================================================="
}

# Dispatch command
if [ $# -lt 1 ]; then
    show_help
    exit 1
fi

case "$1" in
    init)
        cmd_init "$@"
        ;;
    recon)
        cmd_recon
        ;;
    validate)
        cmd_validate
        ;;
    doctor)
        cmd_doctor
        ;;
    commit)
        cmd_commit "$@"
        ;;
    sync-git)
        cmd_sync_git
        ;;
    lock)
        cmd_lock "${2:-}"
        ;;
    unlock)
        cmd_unlock "${2:-}"
        ;;
    archive)
        cmd_archive
        ;;
    migrate)
        cmd_migrate
        ;;
    build)
        cmd_build
        ;;
    lint)
        cmd_lint
        ;;
    test)
        cmd_test
        ;;
    sync-api)
        cmd_sync_api
        ;;
    log-usage)
        cmd_log_usage "$@"
        ;;
    create-adr)
        cmd_create_adr "$@"
        ;;
    release)
        cmd_release "$@"
        ;;
    create-skill)
        cmd_create_skill "$@"
        ;;
    list-skills)
        cmd_list_skills
        ;;
    create-rule)
        cmd_create_rule "$@"
        ;;
    list-rules)
        cmd_list_rules
        ;;
    git-profile)
        cmd_git_profile "$@"
        ;;
    api-profile)
        cmd_api_profile "$@"
        ;;
    help)
        show_help
        ;;
    *)
        echo "Unknown command: $1" >&2
        show_help
        exit 1
        ;;
esac
